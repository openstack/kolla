#!/usr/bin/env python

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

# TODO(SamYaple): Allow image pushing
# TODO(SamYaple): Single image building w/ optional parent building
# TODO(SamYaple): Build only missing images
# TODO(SamYaple): Execute the source install script that will pull
#                 down and create tarball
# TODO(jpeeler): Add clean up handler for SIGINT

import argparse
import ConfigParser
import datetime
import json
import logging
import os
import Queue
import requests
import shutil
import signal
import sys
import tempfile
from threading import Thread
import time
import traceback

import docker
import jinja2

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

signal.signal(signal.SIGINT, signal.SIG_DFL)


class WorkerThread(Thread):

    def __init__(self, queue, nocache, keep, threads):
        self.queue = queue
        self.nocache = nocache
        self.forcerm = not keep
        self.threads = threads
        self.dc = docker.Client(**docker.utils.kwargs_from_env())
        Thread.__init__(self)

    def run(self):
        """Executes tasks until the queue is empty"""
        while True:
            try:
                data = self.queue.get(block=False)
                self.builder(data)
                self.queue.task_done()
            except Queue.Empty:
                break
            except Exception:
                traceback.print_exc()
                self.queue.task_done()

    def process_source(self, source, dest_dir):
        if source['type'] == 'url':
            r = requests.get(source['source'])

            if r.status_code == 200:
                with open(os.path.join(dest_dir, source['dest']), 'wb') as f:
                    f.write(r.content)
            else:
                LOG.error(
                    'Failed to download tarball: status_code {}'.format(
                        r.status_code))

    def builder(self, image):
        LOG.info('Processing: {}'.format(image['name']))
        image['status'] = "building"

        if (image['parent'] is not None and
                image['parent']['status'] == "error"):
            image['status'] = "parent_error"
            return

        if image['source']:
            self.process_source(image['source'], image['path'])

        # Pull the latest image for the base distro only
        pull = True if image['parent'] is None else False

        image['logs'] = str()
        for response in self.dc.build(path=image['path'],
                                      tag=image['fullname'],
                                      nocache=self.nocache,
                                      rm=True,
                                      pull=pull,
                                      forcerm=self.forcerm):
            stream = json.loads(response)

            if 'stream' in stream:
                image['logs'] = image['logs'] + stream['stream']
                if self.threads == 1:
                    LOG.info('{}:{}'.format(image['name'],
                                            stream['stream'].rstrip()))

            if 'errorDetail' in stream:
                image['status'] = "error"
                LOG.error(stream['errorDetail']['message'])
                raise Exception(stream['errorDetail']['message'])

        image['status'] = "built"

        if self.threads == 1:
            LOG.info('Processed: {}'.format(image['name']))
        else:
            LOG.info('{}Processed: {}'.format(image['logs'], image['name']))


def argParser():
    parser = argparse.ArgumentParser(description='Kolla build script')
    parser.add_argument('-n', '--namespace',
                        help='Set the Docker namespace name',
                        type=str,
                        default='kollaglue')
    parser.add_argument('--tag',
                        help='Set the Docker tag',
                        type=str,
                        default='latest')
    parser.add_argument('-b', '--base',
                        help='The base distro to use when building',
                        type=str,
                        default='centos')
    parser.add_argument('--base-tag',
                        help='The base distro image tag',
                        type=str,
                        default='latest')
    parser.add_argument('-t', '--type',
                        help='The method of the Openstack install',
                        type=str,
                        default='binary')
    parser.add_argument('--no-cache',
                        help='Do not use the Docker cache when building',
                        action='store_true',
                        default=False)
    parser.add_argument('--keep',
                        help='Keep failed intermediate containers',
                        action='store_true',
                        default=False)
    parser.add_argument('--push',
                        help='Push images after building',
                        action='store_true',
                        default=False)
    parser.add_argument('-T', '--threads',
                        help='The number of threads to use while building.'
                             ' (Note: setting to one will allow real time'
                             ' logging.)',
                        type=int,
                        default=8)
    parser.add_argument('--template',
                        help='Create dockerfiles from templates',
                        action='store_true',
                        default=False)
    parser.add_argument('-d', '--debug',
                        help='Turn on debugging log level',
                        action='store_true')
    return vars(parser.parse_args())


class KollaWorker(object):

    def __init__(self, args):
        self.kolla_dir = os.path.join(sys.path[0], '..')
        self.images_dir = os.path.join(self.kolla_dir, 'docker')
        self.templates_dir = os.path.join(self.kolla_dir, 'docker_templates')
        self.namespace = args['namespace']
        self.template = args['template']
        self.base = args['base']
        self.base_tag = args['base_tag']
        self.type_ = args['type']
        self.tag = args['tag']
        self.prefix = self.base + '-' + self.type_ + '-'
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(os.path.join(sys.path[0], '..', 'build.ini'))

        self.image_statuses_bad = {}
        self.image_statuses_good = {}

    def setupWorkingDir(self):
        """Creates a working directory for use while building"""
        ts = time.time()
        ts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S_')
        self.temp_dir = tempfile.mkdtemp(prefix='kolla-' + ts)
        self.working_dir = os.path.join(self.temp_dir, 'docker')
        if self.template:
            shutil.copytree(self.templates_dir, self.working_dir)
        else:
            shutil.copytree(self.images_dir, self.working_dir)
        LOG.debug('Created working dir: {}'.format(self.working_dir))

    def createDockerfiles(self):
        for path in self.docker_build_paths:
            template_name = "Dockerfile.j2"
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
            template = env.get_template(template_name)
            values = {'base_distro': self.base,
                      'base_distro_tag': self.base_tag,
                      'install_type': self.type_,
                      'namespace': self.namespace,
                      'tag': self.tag}
            content = template.render(values)
            with open(os.path.join(path, 'Dockerfile'), 'w') as f:
                f.write(content)

    def findDockerfiles(self):
        """Recursive search for Dockerfiles in the working directory"""
        self.docker_build_paths = list()

        if self.template:
            path = self.working_dir
            filename = 'Dockerfile.j2'
        else:
            path = os.path.join(self.working_dir, self.base, self.type_)
            filename = 'Dockerfile'

        for root, dirs, names in os.walk(path):
            if filename in names:
                self.docker_build_paths.append(root)
                LOG.debug('Found {}'.format(root.split(self.working_dir)[1]))

        LOG.debug('Found {} Dockerfiles'.format(len(self.docker_build_paths)))

    def cleanup(self):
        """Remove temp files"""
        shutil.rmtree(self.temp_dir)

    def sortImages(self):
        """Build images dependency tiers"""
        images_to_process = list(self.images)

        self.tiers = list()
        while images_to_process:
            self.tiers.append(list())
            processed_images = list()

            for image in images_to_process:
                if image['parent'] is None:
                    self.tiers[-1].append(image)
                    processed_images.append(image)
                    LOG.debug('Sorted parentless image: {}'.format(
                        image['name']))
                if len(self.tiers) > 1:
                    for parent in self.tiers[-2]:
                        if image['parent'] == parent['fullname']:
                            image['parent'] = parent
                            self.tiers[-1].append(image)
                            processed_images.append(image)
                            LOG.debug('Sorted image {} with parent {}'.format(
                                image['name'], parent['fullname']))
            LOG.debug('===')
            # TODO(SamYaple): Improve error handling in this section
            if not processed_images:
                LOG.warning('Could not find parent image from some images.'
                            ' Aborting')
                for image in images_to_process:
                    LOG.warning('{} {}'.format(image['name'], image['parent']))
                sys.exit()
            # You cannot modify a list while using the list in a for loop as it
            # will produce unexpected results by messing up the index so we
            # build a seperate list and remove them here instead
            for image in processed_images:
                images_to_process.remove(image)

    def summary(self):
        """Walk the dictionary of images statuses and print results"""
        self.get_image_statuses()
        LOG.info("Successfully built images")
        LOG.info("=========================")
        for name in self.image_statuses_good.keys():
                LOG.info(name)

        LOG.info("Images that failed to build")
        LOG.info("===========================")
        for name, status in self.image_statuses_bad.iteritems():
                LOG.error('{}\r\t\t\t Failed with status: {}'.format(
                    name, status))

    def get_image_statuses(self):
        if len(self.image_statuses_bad) or len(self.image_statuses_good):
            return (self.image_statuses_bad, self.image_statuses_good)
        for image in self.images:
            if image['status'] == "built":
                self.image_statuses_good[image['name']] = image['status']
            else:
                self.image_statuses_bad[image['name']] = image['status']
        return (self.image_statuses_bad, self.image_statuses_good)

    def buildImageList(self):
        self.images = list()

        # Walk all of the Dockerfiles and replace the %%KOLLA%% variables
        for path in self.docker_build_paths:
            with open(os.path.join(path, 'Dockerfile')) as f:
                content = f.read().replace('%%KOLLA_NAMESPACE%%',
                                           self.namespace)
                content = content.replace('%%KOLLA_PREFIX%%', self.prefix)
                content = content.replace('%%KOLLA_TAG%%', self.tag)
            with open(os.path.join(path, 'Dockerfile'), 'w') as f:
                f.write(content)

            image = dict()
            image['status'] = "unprocessed"
            image['name'] = os.path.basename(path)
            image['fullname'] = self.namespace + '/' + self.prefix + \
                image['name'] + ':' + self.tag
            image['path'] = path
            image['parent'] = content.split(' ')[1].split('\n')[0]
            if self.namespace not in image['parent']:
                image['parent'] = None

            if self.type_ == 'source':
                image['source'] = dict()
                try:
                    image['source']['type'] = self.config.get(image['name'],
                                                              'type')
                    image['source']['source'] = self.config.get(image['name'],
                                                                'location')
                    image['source']['dest'] = self.config.get(image['name'],
                                                              'dest_filename')
                except ConfigParser.NoSectionError:
                    LOG.debug('No config found for {}'.format(image['name']))
                    pass

            self.images.append(image)

    def buildQueues(self):
        """Organizes Queue list

        Return a list of Queues that have been organized into a hierarchy
        based on dependencies
        """
        self.buildImageList()
        self.sortImages()

        pools = list()
        for count, tier in enumerate(self.tiers):
            pool = Queue.Queue()
            for image in tier:
                pool.put(image)
                LOG.debug('Tier {}: add image {}'.format(count, image['name']))

            pools.append(pool)

        return pools


def push_image(image):
    dc = docker.Client(**docker.utils.kwargs_from_env())

    image['push_logs'] = str()
    for response in dc.push(image['fullname'],
                            stream=True,
                            insecure_registry=True):
        stream = json.loads(response)

        if 'stream' in stream:
            image['push_logs'] = image['logs'] + stream['stream']
            # This is only single threaded for right now so we can show logs
            print(stream['stream'])
        elif 'errorDetail' in stream:
            image['status'] = "error"
            LOG.error(stream['errorDetail']['message'])


def main():
    args = argParser()
    if args['debug']:
        LOG.setLevel(logging.DEBUG)

    kolla = KollaWorker(args)
    kolla.setupWorkingDir()
    kolla.findDockerfiles()

    if args['template']:
        kolla.createDockerfiles()

    pools = kolla.buildQueues()

    # Returns a list of Queues for us to loop through
    for pool in pools:
        for x in xrange(args['threads']):
            WorkerThread(pool, args['no_cache'], args['keep'],
                         args['threads']).start()
        # block until queue is empty
        pool.join()

    if args['push']:
        for tier in kolla.tiers:
            for image in tier:
                if image['status'] == "built":
                    push_image(image)

    kolla.summary()
    kolla.cleanup()

    return kolla.get_image_statuses()

if __name__ == '__main__':
    main()
