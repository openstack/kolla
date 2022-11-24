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

import datetime
import docker
import errno
import os
import shutil
import tarfile

import git
import requests
from requests import exceptions as requests_exc

from kolla.common import task  # noqa
from kolla.common import utils  # noqa
from kolla.image.utils import Status
from kolla.image.utils import STATUS_ERRORS


class ArchivingError(Exception):
    pass


class DockerTask(task.Task):

    docker_kwargs = docker.utils.kwargs_from_env()

    def __init__(self):
        super(DockerTask, self).__init__()
        self._dc = None

    @property
    def dc(self):
        if self._dc is not None:
            return self._dc
        docker_kwargs = self.docker_kwargs.copy()
        self._dc = docker.APIClient(version='auto', **docker_kwargs)
        return self._dc


class PushIntoQueueTask(task.Task):
    """Task that pushes some other task into a queue."""

    def __init__(self, push_task, push_queue):
        super(PushIntoQueueTask, self).__init__()
        self.push_task = push_task
        self.push_queue = push_queue

    @property
    def name(self):
        return 'PushIntoQueueTask(%s)' % (self.push_task.name)

    def run(self):
        self.push_queue.put(self.push_task)
        self.success = True


class PushError(Exception):
    """Raised when there is a problem with pushing image to repository."""
    pass


class PushTask(DockerTask):
    """Task that pushes an image to a docker repository."""

    def __init__(self, conf, image):
        super(PushTask, self).__init__()
        self.conf = conf
        self.image = image
        self.logger = image.logger

    @property
    def name(self):
        return 'PushTask(%s)' % self.image.name

    def run(self):
        image = self.image
        self.logger.info('Trying to push the image')
        try:
            self.push_image(image)
        except requests_exc.ConnectionError:
            self.logger.exception('Make sure Docker is running and that you'
                                  ' have the correct privileges to run Docker'
                                  ' (root)')
            image.status = Status.CONNECTION_ERROR
        except PushError as exception:
            self.logger.error(exception)
            image.status = Status.PUSH_ERROR
        except Exception:
            self.logger.exception('Unknown error when pushing')
            image.status = Status.PUSH_ERROR
        finally:
            if (image.status not in STATUS_ERRORS and
                    image.status != Status.UNPROCESSED):
                self.logger.info('Pushed successfully')
                self.success = True
            else:
                self.success = False

    def push_image(self, image):
        kwargs = dict(stream=True, decode=True)

        for response in self.dc.push(image.canonical_name, **kwargs):
            if 'stream' in response:
                self.logger.info(response['stream'])
            elif 'errorDetail' in response:
                raise PushError(response['errorDetail']['message'])

        # Reset any previous errors.
        image.status = Status.BUILT


class BuildTask(DockerTask):
    """Task that builds out an image."""

    def __init__(self, conf, image, push_queue):
        super(BuildTask, self).__init__()
        self.conf = conf
        self.image = image
        self.push_queue = push_queue
        self.forcerm = not conf.keep
        self.logger = image.logger

    @property
    def name(self):
        return 'BuildTask(%s)' % self.image.name

    def run(self):
        self.builder(self.image)
        if self.image.status in (Status.BUILT, Status.SKIPPED):
            self.success = True

    @property
    def followups(self):
        followups = []
        if self.conf.push and self.success:
            followups.extend([
                # If we are supposed to push the image into a docker
                # repository, then make sure we do that...
                PushIntoQueueTask(
                    PushTask(self.conf, self.image),
                    self.push_queue),
            ])
        if self.image.children and self.success:
            for image in self.image.children:
                if image.status in (Status.UNMATCHED, Status.SKIPPED,
                                    Status.UNBUILDABLE):
                    continue
                followups.append(BuildTask(self.conf, image, self.push_queue))
        return followups

    def process_source(self, image, source):
        if not source['enabled']:
            self.logger.debug("Skipping disabled source %s", source['name'])
            return

        dest_archive = os.path.join(image.path, source['name'] + '-archive')

        # NOTE(mgoddard): Change ownership of files to root:root. This
        # avoids an issue introduced by the fix for git CVE-2022-24765,
        # which breaks PBR when the source checkout is not owned by the
        # user installing it. LP#1969096
        def reset_userinfo(tarinfo):
            tarinfo.uid = tarinfo.gid = 0
            tarinfo.uname = tarinfo.gname = "root"
            return tarinfo

        if source.get('type') == 'url':
            self.logger.debug("Getting archive from %s", source['source'])
            try:
                r = requests.get(source['source'], timeout=self.conf.timeout)
            except requests_exc.Timeout:
                self.logger.exception(
                    'Request timed out while getting archive from %s',
                    source['source'])
                image.status = Status.ERROR
                return

            if r.status_code == 200:
                with open(dest_archive, 'wb') as f:
                    f.write(r.content)
            else:
                self.logger.error(
                    'Failed to download archive: status_code %s',
                    r.status_code)
                image.status = Status.ERROR
                return

        elif source.get('type') == 'git':
            clone_dir = '{}-{}'.format(dest_archive,
                                       source['reference'].replace('/', '-'))
            if os.path.exists(clone_dir):
                self.logger.info("Clone dir %s exists. Removing it.",
                                 clone_dir)
                shutil.rmtree(clone_dir)

            try:
                self.logger.debug("Cloning from %s", source['source'])
                git.Git().clone(source['source'], clone_dir)
                git.Git(clone_dir).checkout(source['reference'])
                reference_sha = git.Git(clone_dir).rev_parse('HEAD')
                self.logger.debug("Git checkout by reference %s (%s)",
                                  source['reference'], reference_sha)
            except Exception as e:
                self.logger.error("Failed to get source from git: %s",
                                  source['source'])
                self.logger.error("Error: %s", e)
                # clean-up clone folder to retry
                shutil.rmtree(clone_dir)
                image.status = Status.ERROR
                return

            with tarfile.open(dest_archive, 'w') as tar:
                tar.add(clone_dir, arcname=os.path.basename(clone_dir),
                        filter=reset_userinfo)

        elif source.get('type') == 'local':
            self.logger.debug("Getting local archive from %s",
                              source['source'])
            if os.path.isdir(source['source']):
                with tarfile.open(dest_archive, 'w') as tar:
                    tar.add(source['source'],
                            arcname=os.path.basename(source['source']),
                            filter=reset_userinfo)
            else:
                shutil.copyfile(source['source'], dest_archive)

        else:
            self.logger.error("Wrong source type '%s'", source.get('type'))
            image.status = Status.ERROR
            return

        # Set time on destination archive to epoch 0
        os.utime(dest_archive, (0, 0))

        return dest_archive

    def update_buildargs(self):
        buildargs = dict()
        if self.conf.build_args:
            buildargs = dict(self.conf.build_args)

        proxy_vars = ('HTTP_PROXY', 'http_proxy', 'HTTPS_PROXY',
                      'https_proxy', 'FTP_PROXY', 'ftp_proxy',
                      'NO_PROXY', 'no_proxy')

        for proxy_var in proxy_vars:
            if proxy_var in os.environ and proxy_var not in buildargs:
                buildargs[proxy_var] = os.environ.get(proxy_var)

        if not buildargs:
            return None
        return buildargs

    def builder(self, image):

        def make_an_archive(items, arcname, item_child_path=None):
            if not item_child_path:
                item_child_path = arcname
            archives = list()
            items_path = os.path.join(image.path, item_child_path)
            for item in items:
                archive_path = self.process_source(image, item)
                if image.status in STATUS_ERRORS:
                    raise ArchivingError
                if archive_path:
                    archives.append(archive_path)
            if archives:
                for archive in archives:
                    with tarfile.open(archive, 'r') as archive_tar:
                        archive_tar.extractall(path=items_path)
            else:
                try:
                    os.mkdir(items_path)
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        self.logger.info(
                            'Directory %s already exist. Skipping.',
                            items_path)
                    else:
                        self.logger.error('Failed to create directory %s: %s',
                                          items_path, e)
                        image.status = Status.CONNECTION_ERROR
                        raise ArchivingError
            arc_path = os.path.join(image.path, '%s-archive' % arcname)

            # NOTE(jneumann): Change ownership of files to root:root. This
            # avoids an issue introduced by the fix for git CVE-2022-24765,
            # which breaks PBR when the source checkout is not owned by the
            # user installing it. LP#1969096
            def reset_userinfo(tarinfo):
                tarinfo.uid = tarinfo.gid = 0
                tarinfo.uname = tarinfo.gname = "root"
                return tarinfo

            with tarfile.open(arc_path, 'w') as tar:
                tar.add(items_path, arcname=arcname, filter=reset_userinfo)
            return len(os.listdir(items_path))

        self.logger.debug('Processing')

        if image.status in [Status.SKIPPED, Status.UNBUILDABLE]:
            self.logger.info('Skipping %s' % image.name)
            return

        if image.status == Status.UNMATCHED:
            return

        if (image.parent is not None and
                image.parent.status in STATUS_ERRORS):
            self.logger.error('Parent image error\'d with message "%s"',
                              image.parent.status)
            image.status = Status.PARENT_ERROR
            return

        image.status = Status.BUILDING
        image.start = datetime.datetime.now()
        self.logger.info('Building started at %s' % image.start)

        if image.source and 'source' in image.source:
            self.process_source(image, image.source)
            if image.status in STATUS_ERRORS:
                return

        try:
            plugins_am = make_an_archive(image.plugins, 'plugins')
        except ArchivingError:
            self.logger.error(
                "Failed turning any plugins into a plugins archive")
            return
        else:
            self.logger.debug(
                "Turned %s plugins into plugins archive",
                plugins_am)
        try:
            additions_am = make_an_archive(image.additions, 'additions')
        except ArchivingError:
            self.logger.error(
                "Failed turning any additions into a additions archive")
            return
        else:
            self.logger.debug(
                "Turned %s additions into additions archive",
                additions_am)

        # Pull the latest image for the base distro only
        pull = self.conf.pull if image.parent is None else False

        buildargs = self.update_buildargs()
        try:
            for stream in self.dc.build(path=image.path,
                                        tag=image.canonical_name,
                                        nocache=not self.conf.cache,
                                        rm=True,
                                        decode=True,
                                        network_mode=self.conf.network_mode,
                                        pull=pull,
                                        forcerm=self.forcerm,
                                        buildargs=buildargs):
                if 'stream' in stream:
                    for line in stream['stream'].split('\n'):
                        if line:
                            self.logger.info('%s', line)
                if 'errorDetail' in stream:
                    image.status = Status.ERROR
                    self.logger.error('Error\'d with the following message')
                    for line in stream['errorDetail']['message'].split('\n'):
                        if line:
                            self.logger.error('%s', line)
                    return

            if image.status != Status.ERROR and self.conf.squash:
                self.squash()
        except docker.errors.DockerException:
            image.status = Status.ERROR
            self.logger.exception('Unknown docker error when building')
        except Exception:
            image.status = Status.ERROR
            self.logger.exception('Unknown error when building')
        else:
            image.status = Status.BUILT
            now = datetime.datetime.now()
            self.logger.info('Built at %s (took %s)' %
                             (now, now - image.start))

    def squash(self):
        image_tag = self.image.canonical_name
        image_id = self.dc.inspect_image(image_tag)['Id']

        parent_history = self.dc.history(self.image.parent_name)
        parent_last_layer = parent_history[0]['Id']
        self.logger.info('Parent lastest layer is: %s' % parent_last_layer)

        utils.squash(image_id, image_tag, from_layer=parent_last_layer,
                     cleanup=self.conf.squash_cleanup,
                     tmp_dir=self.conf.squash_tmp_dir)
        self.logger.info('Image is squashed successfully')
