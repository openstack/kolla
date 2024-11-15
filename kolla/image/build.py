# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import logging
import queue
import shutil
import sys
import threading
import time

from kolla.common import config as common_config
from kolla.common import utils
from kolla.engine_adapter import engine
from kolla.image.kolla_worker import KollaWorker
from kolla.image.utils import LOG
from kolla.image.utils import Status
from oslo_config import cfg


@contextlib.contextmanager
def join_many(threads):
    try:
        yield
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        try:
            LOG.info('Waiting for daemon threads exit. Push Ctrl + c again to'
                     ' force exit')
            for t in threads:
                if t.is_alive():
                    LOG.debug('Waiting thread %s to exit', t.name)
                    # NOTE(Jeffrey4l): Python Bug: When join without timeout,
                    # KeyboardInterrupt is never sent.
                    t.join(0xffff)
                LOG.debug('Thread %s exits', t.name)
        except KeyboardInterrupt:
            LOG.warning('Force exits')


class WorkerThread(threading.Thread):
    """Thread that executes tasks until the queue provides a tombstone."""

    #: Object to be put on worker queues to get them to die.
    tombstone = object()

    def __init__(self, conf, queue):
        super(WorkerThread, self).__init__()
        self.queue = queue
        self.conf = conf
        self.should_stop = False

    def run(self):
        while not self.should_stop:
            task = self.queue.get()
            if task is self.tombstone:
                # Ensure any other threads also get the tombstone.
                self.queue.put(task)
                break
            try:
                for attempt in range(self.conf.retries + 1):
                    if self.should_stop:
                        break
                    LOG.info("Attempt number: %s to run task: %s ",
                             attempt + 1, task.name)
                    try:
                        task.run()
                        if task.success:
                            break
                    except Exception:
                        LOG.exception('Unhandled error when running %s',
                                      task.name)
                    # try again...
                    task.reset()
                if task.success and not self.should_stop:
                    for next_task in task.followups:
                        LOG.info('Added next task %s to queue',
                                 next_task.name)
                        self.queue.put(next_task)
            finally:
                self.queue.task_done()


def run_build():
    """Build container images.

    :return: A 6-tuple containing bad, good, unmatched, skipped,
    unbuildable and allowed to fail container image status dicts,
    or None if no images were built.
    """
    conf = cfg.ConfigOpts()
    common_config.parse(conf, sys.argv[1:], prog='kolla-build')

    if conf.debug:
        LOG.setLevel(logging.DEBUG)

    if conf.engine not in (engine.Engine.DOCKER.value,
                           engine.Engine.PODMAN.value):
        LOG.error(f'Unsupported engine name "{conf.engine}", exiting.')
        sys.exit(1)
    LOG.info(f'Using engine: {conf.engine}')

    if conf.engine == engine.Engine.DOCKER.value:
        try:
            import docker
            docker.__version__
        except ImportError as e:
            LOG.error("Error, you have set Docker as container engine, "
                      "but the Python library is not found."
                      "Try running 'pip install docker'\n"
                      "Python error: %s", e)
            sys.exit(1)
        if conf.squash:
            squash_version = utils.get_docker_squash_version()
            LOG.info('Image squash is enabled and "docker-squash" version '
                     'is %s', squash_version)

    if conf.engine == engine.Engine.PODMAN.value:
        try:
            import podman
            podman.__version__
        except ImportError as e:
            LOG.error("Error, you have set Podman as container engine, "
                      "but the Python library is not found."
                      "Try running 'pip install podman'\n"
                      "Python error: %s", e)
            exit(1)

    kolla = KollaWorker(conf)
    kolla.setup_working_dir()
    kolla.find_dockerfiles()
    kolla.create_dockerfiles()
    kolla.create_patch_files()
    kolla.build_image_list()
    kolla.find_parents()
    kolla.filter_images()

    if conf.template_only:
        for image in kolla.images:
            if image.status == Status.MATCHED:
                continue

            shutil.rmtree(image.path)

        LOG.info('Dockerfiles are generated in %s', kolla.working_dir)
        return

    # We set the atime and mtime to 0 epoch to preserve allow the Docker cache
    # to work like we want. A different size or hash will still force a rebuild
    kolla.set_time()

    if conf.save_dependency:
        kolla.save_dependency(conf.save_dependency)
        LOG.info('Container images dependency are saved in %s',
                 conf.save_dependency)
        return
    if conf.list_images:
        kolla.list_images()
        return
    if conf.list_dependencies:
        kolla.list_dependencies()
        return

    push_queue = queue.Queue()
    build_queue = kolla.build_queue(push_queue)
    workers = []

    with join_many(workers):
        try:
            for _ in range(conf.threads):
                worker = WorkerThread(conf, build_queue)
                worker.daemon = True
                worker.start()
                workers.append(worker)

            for _ in range(conf.push_threads):
                worker = WorkerThread(conf, push_queue)
                worker.daemon = True
                worker.start()
                workers.append(worker)

            # sleep until build_queue is empty
            while build_queue.unfinished_tasks or push_queue.unfinished_tasks:
                time.sleep(3)

            # ensure all threads exited happily
            push_queue.put(WorkerThread.tombstone)
            build_queue.put(WorkerThread.tombstone)
        except KeyboardInterrupt:
            for w in workers:
                w.should_stop = True
            push_queue.put(WorkerThread.tombstone)
            build_queue.put(WorkerThread.tombstone)
            raise

    if conf.summary:
        kolla.summary()
    kolla.cleanup()
    return kolla.get_image_statuses()
