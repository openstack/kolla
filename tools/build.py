#!/usr/bin/env python

#TODO(SamYaple): Allow image pushing
#TODO(SamYaple): Single image building w/ optional parent building
#TODO(SamYaple): Build only missing images
#TODO(SamYaple): Execute the source install script that will pull down and create tarball
#TODO(SamYaple): Improve logging instead of printing to stdout

from __future__ import print_function
import argparse
import datetime
import json
import os
import Queue
import shutil
import sys
import tempfile
from threading import Thread
import time
import traceback

import docker

class WorkerThread(Thread):
    def __init__(self, queue, cache, rm):
        self.queue = queue
        self.nocache = not cache
        self.forcerm = rm
        self.dc = docker.Client()
        Thread.__init__(self)

    def run(self):
        """ Executes tasks until the queue is empty """
        while True:
            try:
                data = self.queue.get(block=False)
                self.builder(data)
                self.queue.task_done()
            except Queue.Empty:
                break
            except:
                traceback.print_exc()
                self.queue.task_done()

    def builder(self, image):
        print('Processing:', image['name'])
        image['status'] = "building"

        if image['parent'] != None and image['parent']['status'] == "error":
            image['status'] = "parent_error"
            return

        # Pull the latest image for the base distro only
        pull = True if image['parent'] == None else False

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
            elif 'errorDetail' in stream:
                image['status'] = "error"
                raise Exception(stream['errorDetail']['message'])

        image['status'] = "built"
        print(image['logs'], '\nProcessed:', image['name'])

def argParser():
    parser = argparse.ArgumentParser(description='Kolla build script')
    parser.add_argument('-n','--namespace',
                        help='Set the Docker namespace name',
                        type=str,
                        default='kollaglue')
    parser.add_argument('--tag',
                        help='Set the Docker tag',
                        type=str,
                        default='latest')
    parser.add_argument('-b','--base',
                        help='The base distro to use when building',
                        type=str,
                        default='centos')
    parser.add_argument('-t','--type',
                        help='The method of the Openstack install',
                        type=str,
                        default='binary')
    parser.add_argument('-c','--cache',
                        help='Use Docker cache when building',
                        type=bool,
                        default=True)
    parser.add_argument('-r','--rm',
                        help='Remove intermediate containers while building',
                        type=bool,
                        default=True)
    parser.add_argument('-T','--threads',
                        help='The number of threads to use while building',
                        type=int,
                        default=8)
    return vars(parser.parse_args())

class KollaWorker():
    def __init__(self, args):
        self.kolla_dir = os.path.join(sys.path[0], '..')
        self.images_dir = os.path.join(self.kolla_dir, 'docker')

        self.namespace = args['namespace']
        self.base = args['base']
        self.type_ = args['type']
        self.tag = args['tag']
        self.prefix = self.base + '-' + self.type_ + '-'

    def setupWorkingDir(self):
        """ Creates a working directory for use while building """
        ts = time.time()
        ts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S_')
        self.temp_dir = tempfile.mkdtemp(prefix='kolla-' + ts)
        self.working_dir = os.path.join(self.temp_dir, 'docker')
        shutil.copytree(self.images_dir, self.working_dir)

    def findDockerfiles(self):
        """ Recursive search for Dockerfiles in the working directory """
        self.docker_build_paths = list()
        path = os.path.join(self.working_dir, self.base, self.type_)

        for root, dirs, names in os.walk(path):
            if 'Dockerfile' in names:
                self.docker_build_paths.append(root)

    def cleanup(self):
        """ Remove temp files """
        shutil.rmtree(self.temp_dir)

    def sortImages(self):
        """ Build images dependency tiers """
        images_to_process = list(self.images)

        self.tiers = list()
        while images_to_process:
            self.tiers.append(list())
            processed_images = list()

            for image in images_to_process:
                if image['parent'] == None:
                    self.tiers[-1].append(image)
                    processed_images.append(image)
                if len(self.tiers) > 1:
                    for parent in self.tiers[-2]:
                        if image['parent'] == parent['fullname']:
                            image['parent'] = parent
                            self.tiers[-1].append(image)
                            processed_images.append(image)

            #TODO(SamYaple): Improve error handling in this section
            if not processed_images:
                print('Could not find parent image from some images. Aborting', file=sys.stderr)
                for image in images_to_process:
                    print(image['name'], image['parent'], file=sys.stderr)
                sys.exit()

            # You cannot modify a list while using the list in a for loop as it
            # will produce unexpected results by messing up the index so we
            # build a seperate list and remove them here instead
            for image in processed_images:
                images_to_process.remove(image)

    def summary(self):
        """ Walk the list of images and check for errors """
        print("Successfully built images")
        print("=========================")
        for image in self.images:
            if image['status'] == "built":
                print(image['name'])

        print("\nImages that failed to build")
        print("===========================")
        for image in self.images:
            if image['status'] != "built":
                print(image['name'], "\r\t\t\t Failed with status:", image['status'])

    def buildImageList(self):
        self.images = list()

        # Walk all of the Dockerfiles and replace the %%KOLLA%% variables
        for path in self.docker_build_paths:
            with open(os.path.join(path, 'Dockerfile')) as f:
                content = f.read().replace('%%KOLLA_NAMESPACE%%', self.namespace)
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
            if not self.namespace in image['parent']:
                image['parent'] = None

            self.images.append(image)

    def buildQueues(self):
        """
           Return a list of Queues that have been organized into a hierarchy
           based on dependencies
        """
        self.buildImageList()
        self.sortImages()

        pools = list()
        for tier in self.tiers:
            pool = Queue.Queue()
            for image in tier:
                pool.put(image)

            pools.append(pool)

        return pools

def main():
    args = argParser()

    kolla = KollaWorker(args)
    kolla.setupWorkingDir()
    kolla.findDockerfiles()

    # Returns a list of Queues for us to loop through
    for pool in kolla.buildQueues():
        for x in xrange(args['threads']):
            WorkerThread(pool, args['cache'], args['rm']).start()
        # block until queue is empty
        pool.join()

    kolla.summary()
    kolla.cleanup()

if __name__ == '__main__':
    main()
