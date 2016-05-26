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

from __future__ import print_function

import datetime
import errno
import graphviz
import json
import logging
import os
import pprint
import re
import requests
import shutil
import signal
import sys
import tarfile
import tempfile
import threading
import time

import docker
import git
import jinja2
from oslo_config import cfg
from requests import exceptions as requests_exc
import six

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../..'))

# NOTE(SamYaple): Update the search patch to prefer PROJECT_ROOT as the source
#                 of packages to import if we are using local tools/build.py
#                 instead of pip installed kolla-build tool
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kolla.common import config as common_config
from kolla.common import task
from kolla import version

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def handle_ctrlc(single, frame):
    kollaobj = frame.f_locals['kolla']
    kollaobj.cleanup()
    sys.exit(1)

signal.signal(signal.SIGINT, handle_ctrlc)


class KollaDirNotFoundException(Exception):
    pass


class KollaUnknownBuildTypeException(Exception):
    pass


class KollaMismatchBaseTypeException(Exception):
    pass


class KollaRpmSetupUnknownConfig(Exception):
    pass


def docker_client():
    try:
        docker_kwargs = docker.utils.kwargs_from_env()
        return docker.Client(version='auto', **docker_kwargs)
    except docker.errors.DockerException:
        LOG.exception('Can not communicate with docker service.'
                      'Please check docker service is running without errors')
        sys.exit(1)


class PushIntoQueueTask(task.Task):
    """Task that pushes some other task into a queue."""

    def __init__(self, push_task, push_queue):
        super(PushIntoQueueTask, self).__init__()
        self.push_task = push_task
        self.push_queue = push_queue

    @property
    def name(self):
        return 'PushIntoQueueTask(%s=>%s)' % (self.push_task.name,
                                              self.push_queue)

    def run(self):
        self.push_queue.put(self.push_task)
        self.success = True


class PushTask(task.Task):
    """Task that pushes a image to a docker repository."""

    def __init__(self, conf, image):
        super(PushTask, self).__init__()
        self.dc = docker_client()
        self.conf = conf
        self.image = image

    @property
    def name(self):
        return 'PushTask(%s)' % self.image['name']

    def run(self):
        image = self.image
        try:
            LOG.debug('%s:Try to push the image', image['name'])
            self.push_image(image)
        except requests_exc.ConnectionError:
            LOG.exception('%s:Make sure Docker is running and that you'
                          ' have the correct privileges to run Docker'
                          ' (root)', image['name'])
            image['status'] = "connection_error"
        except Exception:
            LOG.exception('%s:Unknown error when pushing', image['name'])
            image['status'] = "push_error"
        finally:
            if "error" not in image['status']:
                LOG.info('%s:Pushed successfully', image['name'])
                self.success = True
            else:
                self.success = False

    def push_image(self, image):
        image['push_logs'] = str()

        for response in self.dc.push(image['fullname'],
                                     stream=True,
                                     insecure_registry=True):
            stream = json.loads(response)

            if 'stream' in stream:
                image['push_logs'] = image['logs'] + stream['stream']
                LOG.info('%s', stream['stream'])
            elif 'errorDetail' in stream:
                image['status'] = "error"
                LOG.error(stream['errorDetail']['message'])


class BuildTask(task.Task):
    """Task that builds out an image."""

    def __init__(self, conf, image, push_queue):
        super(BuildTask, self).__init__()
        self.conf = conf
        self.image = image
        self.dc = docker_client()
        self.push_queue = push_queue
        self.nocache = not conf.cache or conf.no_cache
        self.forcerm = not conf.keep

    @property
    def name(self):
        return 'BuildTask(%s)' % self.image['name']

    def run(self):
        self.builder(self.image)
        if self.image['status'] == 'built':
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
        if self.image['children'] and self.success:
            for image in self.image['children']:
                followups.append(BuildTask(self.conf, image, self.push_queue))
        return followups

    def process_source(self, image, source):
        dest_archive = os.path.join(image['path'], source['name'] + '-archive')

        if source.get('type') == 'url':
            LOG.debug("%s:Getting archive from %s", image['name'],
                      source['source'])
            try:
                r = requests.get(source['source'], timeout=self.conf.timeout)
            except requests_exc.Timeout:
                LOG.exception('Request timed out while getting archive'
                              ' from %s', source['source'])
                image['status'] = "error"
                image['logs'] = str()
                return

            if r.status_code == 200:
                with open(dest_archive, 'wb') as f:
                    f.write(r.content)
            else:
                LOG.error('%s:Failed to download archive: status_code %s',
                          image['name'], r.status_code)
                image['status'] = "error"
                return

        elif source.get('type') == 'git':
            clone_dir = '{}-{}'.format(dest_archive,
                                       source['reference'].replace('/', '-'))
            try:
                LOG.debug("%s:Cloning from %s", image['name'],
                          source['source'])
                git.Git().clone(source['source'], clone_dir)
                git.Git(clone_dir).checkout(source['reference'])
                reference_sha = git.Git(clone_dir).rev_parse('HEAD')
                LOG.debug("%s:Git checkout by reference %s (%s)",
                          image['name'], source['reference'], reference_sha)
            except Exception as e:
                LOG.error("%s:Failed to get source from git", image['name'])
                LOG.error("%s:Error:%s", image['name'], str(e))
                # clean-up clone folder to retry
                shutil.rmtree(clone_dir)
                image['status'] = "error"
                return

            with tarfile.open(dest_archive, 'w') as tar:
                tar.add(clone_dir, arcname=os.path.basename(clone_dir))

        elif source.get('type') == 'local':
            LOG.debug("%s:Getting local archive from %s", image['name'],
                      source['source'])
            if os.path.isdir(source['source']):
                with tarfile.open(dest_archive, 'w') as tar:
                    tar.add(source['source'],
                            arcname=os.path.basename(source['source']))
            else:
                shutil.copyfile(source['source'], dest_archive)

        else:
            LOG.error("%s:Wrong source type '%s'", image['name'],
                      source.get('type'))
            image['status'] = "error"
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
        LOG.debug('%s:Processing', image['name'])
        if image['status'] == 'unmatched':
            return

        if (image['parent'] is not None and
                image['parent']['status'] in ['error', 'parent_error',
                                              'connection_error']):
            LOG.error('%s:Parent image error\'d with message "%s"',
                      image['name'], image['parent']['status'])
            image['status'] = "parent_error"
            return

        image['status'] = "building"
        LOG.info('%s:Building', image['name'])

        if 'source' in image and 'source' in image['source']:
            self.process_source(image, image['source'])
            if image['status'] == "error":
                return

        plugin_archives = list()
        plugins_path = os.path.join(image['path'], 'plugins')
        for plugin in image['plugins']:
            archive_path = self.process_source(image, plugin)
            if image['status'] == "error":
                return
            plugin_archives.append(archive_path)
        if plugin_archives:
            for plugin_archive in plugin_archives:
                with tarfile.open(plugin_archive, 'r') as plugin_archive_tar:
                    plugin_archive_tar.extractall(path=plugins_path)
        else:
            try:
                os.mkdir(plugins_path)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    LOG.info('Directory %s already exist. Skipping.',
                             plugins_path)
                else:
                    LOG.error('Failed to create directory %s: %s',
                              plugins_path, e)
                    image['status'] = "error"
                    return
        with tarfile.open(os.path.join(image['path'], 'plugins-archive'),
                          'w') as tar:
            tar.add(plugins_path, arcname='plugins')

        # Pull the latest image for the base distro only
        pull = True if image['parent'] is None else False

        image['logs'] = str()
        buildargs = self.update_buildargs()
        for response in self.dc.build(path=image['path'],
                                      tag=image['fullname'],
                                      nocache=self.nocache,
                                      rm=True,
                                      pull=pull,
                                      forcerm=self.forcerm,
                                      buildargs=buildargs):
            stream = json.loads(response.decode('utf-8'))

            if 'stream' in stream:
                image['logs'] = image['logs'] + stream['stream']
                for line in stream['stream'].split('\n'):
                    if line:
                        LOG.info('%s:%s', image['name'], line)

            if 'errorDetail' in stream:
                image['status'] = "error"
                LOG.error('%s:Error\'d with the following message',
                          image['name'])
                for line in stream['errorDetail']['message'].split('\n'):
                    if line:
                        LOG.error('%s:%s', image['name'], line)
                return

        image['status'] = "built"

        LOG.info('%s:Built', image['name'])


class WorkerThread(threading.Thread):
    """Thread that executes tasks until the queue provides a tombstone."""

    #: Object to be put on worker queues to get them to die.
    tombstone = object()

    def __init__(self, conf, queue):
        super(WorkerThread, self).__init__()
        self.queue = queue
        self.conf = conf

    def run(self):
        while True:
            task = self.queue.get()
            if task is self.tombstone:
                # Ensure any other threads also get the tombstone.
                self.queue.put(task)
                break
            try:
                for attempt in six.moves.range(self.conf.retries + 1):
                    if attempt > 0:
                        LOG.debug("Attempting to run task %s for the %s time",
                                  task.name, attempt + 1)
                    else:
                        LOG.debug("Attempting to run task %s for the first"
                                  " time", task.name)
                    try:
                        task.run()
                        if task.success:
                            break
                    except Exception:
                        LOG.exception('Unhandled error when running %s',
                                      task.name)
                    # try again...
                    task.reset()
                if task.success:
                    for next_task in task.followups:
                        LOG.debug('Added next task %s to queue',
                                  next_task.name)
                        self.queue.put(next_task)
            finally:
                self.queue.task_done()


class KollaWorker(object):

    def __init__(self, conf):
        self.conf = conf
        self.images_dir = self._get_images_dir()
        self.registry = conf.registry
        if self.registry:
            self.namespace = self.registry + '/' + conf.namespace
        else:
            self.namespace = conf.namespace
        self.base = conf.base
        self.base_tag = conf.base_tag
        self.install_type = conf.install_type
        self.tag = conf.tag
        self.images = list()
        rpm_setup_config = filter(None, conf.rpm_setup_config)
        self.rpm_setup = self.build_rpm_setup(rpm_setup_config)

        rh_base = ['fedora', 'centos', 'oraclelinux', 'rhel']
        rh_type = ['source', 'binary', 'rdo', 'rhos']
        deb_base = ['ubuntu', 'debian']
        deb_type = ['source', 'binary']

        if not ((self.base in rh_base and self.install_type in rh_type) or
                (self.base in deb_base and self.install_type in deb_type)):
            raise KollaMismatchBaseTypeException(
                '{} is unavailable for {}'.format(self.install_type, self.base)
            )

        if self.install_type == 'binary':
            self.install_metatype = 'rdo'
        elif self.install_type == 'source':
            self.install_metatype = 'mixed'
        elif self.install_type == 'rdo':
            self.install_type = 'binary'
            self.install_metatype = 'rdo'
        elif self.install_type == 'rhos':
            self.install_type = 'binary'
            self.install_metatype = 'rhos'
        else:
            raise KollaUnknownBuildTypeException(
                'Unknown install type'
            )

        self.image_prefix = self.base + '-' + self.install_type + '-'

        self.include_header = conf.include_header
        self.include_footer = conf.include_footer
        self.regex = conf.regex
        self.image_statuses_bad = dict()
        self.image_statuses_good = dict()
        self.image_statuses_unmatched = dict()
        self.maintainer = conf.maintainer

    def _get_images_dir(self):
        possible_paths = (
            PROJECT_ROOT,
            os.path.join(sys.prefix, 'share/kolla'),
            os.path.join(sys.prefix, 'local/share/kolla'))

        for path in possible_paths:
            image_path = os.path.join(path, 'docker')
            # NOTE(SamYaple): We explicty check for the base folder to ensure
            #                 this is the correct path
            # TODO(SamYaple): Improve this to make this safer
            if os.path.exists(os.path.join(image_path, 'base')):
                LOG.info('Found the docker image folder at %s', image_path)
                return image_path
        else:
            raise KollaDirNotFoundException('Image dir can not be found')

    def build_rpm_setup(self, rpm_setup_config):
        """Generates a list of docker commands based on provided configuration.

        :param rpm_setup_config: A list of .rpm or .repo paths or URLs
        :return: A list of docker commands
        """
        rpm_setup = list()

        for config in rpm_setup_config:
            if config.endswith('.rpm'):
                # RPM files can be installed with yum from file path or url
                cmd = "RUN yum -y install {}".format(config)
            elif config.endswith('.repo'):
                if config.startswith('http'):
                    # Curl http://url/etc.repo to /etc/yum.repos.d/etc.repo
                    name = config.split('/')[-1]
                    cmd = "RUN curl {} -o /etc/yum.repos.d/{}".format(config,
                                                                      name)
                else:
                    # Copy .repo file from filesystem
                    cmd = "COPY {} /etc/yum.repos.d/".format(config)
            else:
                raise KollaRpmSetupUnknownConfig(
                    'RPM setup must be provided as .rpm or .repo files.'
                    ' Attempted configuration was {}'.format(config)
                )

            rpm_setup.append(cmd)

        return rpm_setup

    def copy_apt_files(self):
        if self.conf.apt_sources_list:
            shutil.copyfile(
                self.conf.apt_sources_list,
                os.path.join(self.working_dir, "base", "sources.list")
            )

        if self.conf.apt_preferences:
            shutil.copyfile(
                self.conf.apt_preferences,
                os.path.join(self.working_dir, "base", "apt_preferences")
            )

    def setup_working_dir(self):
        """Creates a working directory for use while building"""
        ts = time.time()
        ts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S_')
        self.temp_dir = tempfile.mkdtemp(prefix='kolla-' + ts)
        self.working_dir = os.path.join(self.temp_dir, 'docker')
        shutil.copytree(self.images_dir, self.working_dir)
        self.copy_apt_files()
        LOG.debug('Created working dir: %s', self.working_dir)

    def set_time(self):
        for root, dirs, files in os.walk(self.working_dir):
            for file_ in files:
                os.utime(os.path.join(root, file_), (0, 0))
            for dir_ in dirs:
                os.utime(os.path.join(root, dir_), (0, 0))
        LOG.debug('Set atime and mtime to 0 for all content in working dir')

    def create_dockerfiles(self):
        kolla_version = version.version_info.cached_version_string()
        supported_distro_release = common_config.DISTRO_RELEASE.get(
            self.base)
        for path in self.docker_build_paths:
            template_name = "Dockerfile.j2"
            env = jinja2.Environment(  # nosec: not used to render HTML
                loader=jinja2.FileSystemLoader(path))
            template = env.get_template(template_name)
            values = {'base_distro': self.base,
                      'base_image': self.conf.base_image,
                      'base_distro_tag': self.base_tag,
                      'supported_distro_release': supported_distro_release,
                      'install_metatype': self.install_metatype,
                      'image_prefix': self.image_prefix,
                      'install_type': self.install_type,
                      'namespace': self.namespace,
                      'tag': self.tag,
                      'maintainer': self.maintainer,
                      'kolla_version': kolla_version,
                      'rpm_setup': self.rpm_setup}
            if self.include_header:
                with open(self.include_header, 'r') as f:
                    values['include_header'] = f.read()
            if self.include_footer:
                with open(self.include_footer, 'r') as f:
                    values['include_footer'] = f.read()
            content = template.render(values)
            with open(os.path.join(path, 'Dockerfile'), 'w') as f:
                f.write(content)

    def find_dockerfiles(self):
        """Recursive search for Dockerfiles in the working directory"""
        self.docker_build_paths = list()
        path = self.working_dir
        filename = 'Dockerfile.j2'

        for root, dirs, names in os.walk(path):
            if filename in names:
                self.docker_build_paths.append(root)
                LOG.debug('Found %s', root.split(self.working_dir)[1])

        LOG.debug('Found %d Dockerfiles', len(self.docker_build_paths))

    def cleanup(self):
        """Remove temp files"""
        shutil.rmtree(self.temp_dir)

    def filter_images(self):
        """Filter which images to build"""
        filter_ = list()

        if self.regex:
            filter_ += self.regex
        elif self.conf.profile:
            for profile in self.conf.profile:
                if profile not in self.conf.profiles:
                    self.conf.register_opt(cfg.ListOpt(profile,
                                                       default=[]),
                                           'profiles')
                if len(self.conf.profiles[profile]) == 0:
                    msg = 'Profile: {} does not exist'.format(profile)
                    raise ValueError(msg)
                else:
                    filter_ += self.conf.profiles[profile]

        if filter_:
            patterns = re.compile(r"|".join(filter_).join('()'))
            for image in self.images:
                if image['status'] == 'matched':
                    continue
                if re.search(patterns, image['name']):
                    image['status'] = 'matched'
                    while (image['parent'] is not None and
                           image['parent']['status'] != 'matched'):
                        image = image['parent']
                        image['status'] = 'matched'
                        LOG.debug('%s:Matched regex', image['name'])
                else:
                    image['status'] = 'unmatched'
        else:
            for image in self.images:
                image['status'] = 'matched'

    def summary(self):
        """Walk the dictionary of images statuses and print results"""
        # For debug we print the logs again if the image error'd. This is to
        # to help us debug and it will be extra helpful in the gate.
        for image in self.images:
            if image['status'] == 'error':
                LOG.debug("%s:Failed with the following logs", image['name'])
                for line in image['logs'].split('\n'):
                    if line:
                        LOG.debug("%s:%s", image['name'], ''.join(line))

        self.get_image_statuses()

        if self.image_statuses_good:
            LOG.info("Successfully built images")
            LOG.info("=========================")
            for name in self.image_statuses_good.keys():
                LOG.info(name)

        if self.image_statuses_bad:
            LOG.info("Images that failed to build")
            LOG.info("===========================")
            for name, status in self.image_statuses_bad.items():
                LOG.error('%s Failed with status: %s', name, status)

        if self.image_statuses_unmatched:
            LOG.debug("Images not matched for build by regex")
            LOG.debug("=====================================")
            for name in self.image_statuses_unmatched.keys():
                LOG.debug(name)

    def get_image_statuses(self):
        if any([self.image_statuses_bad,
                self.image_statuses_good,
                self.image_statuses_unmatched]):
            return (self.image_statuses_bad,
                    self.image_statuses_good,
                    self.image_statuses_unmatched)
        for image in self.images:
            if image['status'] == "built":
                self.image_statuses_good[image['name']] = image['status']
            elif image['status'] == "unmatched":
                self.image_statuses_unmatched[image['name']] = image['status']
            else:
                self.image_statuses_bad[image['name']] = image['status']
        return (self.image_statuses_bad,
                self.image_statuses_good,
                self.image_statuses_unmatched)

    def build_image_list(self):
        def process_source_installation(image, section):
            installation = dict()
            # NOTE(jeffrey4l): source is not needed when the type is None
            if self.conf._get('type', self.conf._get_group(section)) is None:
                LOG.debug('%s:No source location found', section)
            else:
                installation['type'] = self.conf[section]['type']
                installation['source'] = self.conf[section]['location']
                installation['name'] = section
                if installation['type'] == 'git':
                    installation['reference'] = self.conf[section]['reference']
            return installation

        for path in self.docker_build_paths:
            # Reading parent image name
            with open(os.path.join(path, 'Dockerfile')) as f:
                content = f.read()

            image = dict()
            image['status'] = "unprocessed"
            image['name'] = os.path.basename(path)
            image['fullname'] = self.namespace + '/' + self.image_prefix + \
                image['name'] + ':' + self.tag
            image['path'] = path
            image['parent_name'] = content.split(' ')[1].split('\n')[0]
            if not image['parent_name'].startswith(self.namespace + '/'):
                image['parent'] = None
            image['children'] = list()
            image['plugins'] = list()

            if self.install_type == 'source':
                # NOTE(jeffrey4l): register the opts if the section didn't
                # register in the kolla/common/config.py file
                if image['name'] not in self.conf._groups:
                    self.conf.register_opts(common_config.get_source_opts(),
                                            image['name'])
                image['source'] = process_source_installation(image,
                                                              image['name'])
                for plugin in [match.group(0) for match in
                               (re.search('{}-plugin-.+'.format(image['name']),
                                          section) for section in
                               self.conf.list_all_sections()) if match]:
                    self.conf.register_opts(common_config.get_source_opts(),
                                            plugin)
                    image['plugins'].append(
                        process_source_installation(image, plugin))

            self.images.append(image)

    def save_dependency(self, to_file):
        dot = graphviz.Digraph(comment='Docker Images Dependency')
        dot.body.extend(['rankdir=LR'])
        for image in self.images:
            if image['status'] not in ['matched']:
                continue
            dot.node(image['name'])
            if image['parent'] is not None:
                dot.edge(image['parent']['name'], image['name'])

        with open(to_file, 'w') as f:
            f.write(dot.source)

    def list_images(self):
        for count, image in enumerate(self.images):
            print(count + 1, ':', image['name'])

    def list_dependencies(self):
        match = False
        for image in self.images:
            if image['status'] in ['matched']:
                match = True
            if image['parent'] is None:
                base = image
        if not match:
            print('Nothing matched!')
            return

        def list_children(images, ancestry):
            children = ancestry.values()[0]
            for item in images:
                if item['status'] not in ['matched']:
                    continue

                if not item['children']:
                    children.append(item['name'])
                else:
                    newparent = {item['name']: []}
                    children.append(newparent)
                    list_children(item['children'], newparent)

        ancestry = {base['name']: []}
        list_children(base['children'], ancestry)
        pprint.pprint(ancestry)

    def find_parents(self):
        """Associate all images with parents and children"""
        sort_images = dict()

        for image in self.images:
            sort_images[image['fullname']] = image

        for parent_name, parent in sort_images.items():
            for image in sort_images.values():
                if image['parent_name'] == parent_name:
                    parent['children'].append(image)
                    image['parent'] = parent

    def build_queue(self, push_queue):
        """Organizes Queue list

        Return a list of Queues that have been organized into a hierarchy
        based on dependencies
        """
        self.build_image_list()
        self.find_parents()
        self.filter_images()

        queue = six.moves.queue.Queue()

        for image in self.images:
            if image['parent'] is None:
                queue.put(BuildTask(self.conf, image, push_queue))
                LOG.debug('%s:Added image to queue', image['name'])

        return queue


def run_build():
    """Build container images.

    :return: A 3-tuple containing bad, good, and unmatched container image
    status dicts, or None if no images were built.
    """
    conf = cfg.ConfigOpts()
    common_config.parse(conf, sys.argv[1:], prog='kolla-build')

    if conf.debug:
        LOG.setLevel(logging.DEBUG)

    kolla = KollaWorker(conf)
    kolla.setup_working_dir()
    kolla.find_dockerfiles()
    kolla.create_dockerfiles()

    if conf.template_only:
        LOG.info('Dockerfiles are generated in %s', kolla.working_dir)
        return

    # We set the atime and mtime to 0 epoch to preserve allow the Docker cache
    # to work like we want. A different size or hash will still force a rebuild
    kolla.set_time()

    if conf.save_dependency:
        kolla.save_dependency(conf.save_dependency)
        LOG.info('Docker images dependency is saved in %s',
                 conf.save_dependency)
        return
    if conf.list_images:
        kolla.list_images()
        return
    if conf.list_dependencies:
        kolla.list_dependencies()
        return

    push_queue = six.moves.queue.Queue()
    queue = kolla.build_queue(push_queue)
    workers = []

    for x in six.moves.range(conf.threads):
        worker = WorkerThread(conf, queue)
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)

    for x in six.moves.range(conf.push_threads):
        worker = WorkerThread(conf, push_queue)
        worker.start()
        workers.append(worker)

    # sleep until queue is empty
    while queue.unfinished_tasks or push_queue.unfinished_tasks:
        time.sleep(3)

    kolla.summary()
    kolla.cleanup()

    # ensure all threads exited happily
    queue.put(WorkerThread.tombstone)
    push_queue.put(WorkerThread.tombstone)
    for w in workers:
        w.join()

    return kolla.get_image_statuses()


def main():
    statuses = run_build()
    if statuses:
        bad_results, good_results, unmatched_results = statuses
        if bad_results:
            return 1
    return 0


if __name__ == '__main__':
    main()
