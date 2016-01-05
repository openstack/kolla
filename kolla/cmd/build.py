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

# TODO(jpeeler): Add clean up handler for SIGINT

import datetime
import errno
import json
import logging
import os
import platform
import re
import requests
import shutil
import signal
import sys
import tarfile
import tempfile
from threading import Thread
import time

import docker
import git
import jinja2
from oslo_config import cfg
from oslo_config import types
from requests.exceptions import ConnectionError
import six

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

signal.signal(signal.SIGINT, signal.SIG_DFL)

RDO_MIRROR = "http://trunk.rdoproject.org/centos7"
DELOREAN = "{}/current/delorean.repo".format(RDO_MIRROR)
DELOREAN_DEPS = "{}/delorean-deps.repo".format(RDO_MIRROR)
INSTALL_TYPE_CHOICES = ['binary', 'source', 'rdo', 'rhos']


class KollaDirNotFoundException(Exception):
    pass


class KollaUnknownBuildTypeException(Exception):
    pass


class KollaRpmSetupUnknownConfig(Exception):
    pass


def docker_client():
    docker_kwargs = docker.utils.kwargs_from_env()
    return docker.Client(version='auto', **docker_kwargs)


class PushThread(Thread):

    def __init__(self, conf, queue):
        super(PushThread, self).__init__()
        self.setDaemon(True)
        self.conf = conf
        self.queue = queue
        self.dc = docker_client()

    def run(self):
        while True:
            try:
                image = self.queue.get()
                LOG.debug('%s:Try to push the image', image['name'])
                self.push_image(image)
                LOG.info('%s:Pushed successfully', image['name'])
            except ConnectionError:
                LOG.exception('%s:Make sure Docker is running and that you'
                              ' have the correct privileges to run Docker'
                              ' (root)', image['name'])
                image['status'] = "connection_error"
            finally:
                self.queue.task_done()

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


class WorkerThread(Thread):

    def __init__(self, queue, push_queue, conf):
        self.conf = conf
        self.queue = queue
        self.push_queue = push_queue
        self.nocache = not conf.cache or conf.no_cache
        self.forcerm = not conf.keep
        self.dc = docker_client()
        super(WorkerThread, self).__init__()

    def end_task(self, image):
        """Properly inform the queue we are finished"""
        # No matter whether the parent failed or not, we still process
        # the children. We have the code in place to catch a parent in
        # an 'error' status
        for child in image['children']:
            self.queue.put(child)
            LOG.debug('%s:Added image to queue', child['name'])
        self.queue.task_done()
        LOG.debug('%s:Processed', image['name'])

    def run(self):
        """Executes tasks until the queue is empty"""
        while True:
            try:
                image = self.queue.get()
                for _ in six.moves.range(self.conf.retries + 1):
                    self.builder(image)
                    if image['status'] in ['built', 'unmatched',
                                           'parent_error']:
                        break
            except ConnectionError:
                LOG.exception('Make sure Docker is running and that you'
                              ' have the correct privileges to run Docker'
                              ' (root)')
                image['status'] = "connection_error"
                break
            self.end_task(image)

    def process_source(self, image, source):
        dest_archive = os.path.join(image['path'], source['name'] + '-archive')

        if source.get('type') == 'url':
            LOG.debug("%s:Getting archive from %s", image['name'],
                      source['source'])
            r = requests.get(source['source'])

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
                LOG.debug("%s:Git checkout by reference %s",
                          image['name'], source['reference'])
                git.Git(clone_dir).checkout(source['reference'])
            except Exception as e:
                LOG.error("%s:Failed to get source from git", image['name'])
                LOG.error("%s:Error:%s", image['name'], str(e))
                # clean-up clone folder to retry
                shutil.rmtree(clone_dir)
                image['status'] = "error"
                return

            with tarfile.open(dest_archive, 'w') as tar:
                tar.add(clone_dir, arcname=os.path.basename(clone_dir))

        else:
            LOG.error("%s:Wrong source type '%s'", image['name'],
                      source.get('type'))
            image['status'] = "error"
            return

        # Set time on destination archive to epoch 0
        os.utime(dest_archive, (0, 0))

        return dest_archive

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
        for response in self.dc.build(path=image['path'],
                                      tag=image['fullname'],
                                      nocache=self.nocache,
                                      rm=True,
                                      pull=pull,
                                      forcerm=self.forcerm):
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
        if self.conf.push:
            self.push_queue.put(image)


def get_kolla_version():
    local_conf_path = os.path.join(find_base_dir(), "setup.cfg")
    config = six.moves.configparser.RawConfigParser()
    config.read(local_conf_path)
    version = config.get("metadata", "version")
    return version


def find_os_type():
    return platform.linux_distribution()


def find_base_dir():
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if os.path.basename(script_path) == 'cmd':
        return os.path.realpath(os.path.join(script_path, '..', '..'))
    if os.path.basename(script_path) == 'bin':
        if find_os_type()[0] in ['Ubuntu', 'debian']:
            return '/usr/local/share/kolla'
        else:
            return '/usr/share/kolla'
    if os.path.exists(os.path.join(script_path, 'tests')):
        return script_path
    raise KollaDirNotFoundException(
        'I do not know where your Kolla directory is'
    )


def find_config_file(filename):
    global_conf_path = os.path.join('/etc/kolla', filename)
    local_conf_path = os.path.join(find_base_dir(), 'etc', 'kolla', filename)

    if os.access(global_conf_path, os.R_OK):
        return global_conf_path
    elif os.access(local_conf_path, os.R_OK):
        return local_conf_path
    else:
        raise KollaDirNotFoundException(
            'Cant find kolla config. Searched at: %s and %s' %
            (global_conf_path, local_conf_path)
        )


class KollaWorker(object):

    def __init__(self, conf):
        self.conf = conf
        self.base_dir = os.path.abspath(find_base_dir())
        LOG.debug("Kolla base directory: " + self.base_dir)
        self.images_dir = os.path.join(self.base_dir, 'docker')

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

    def setup_working_dir(self):
        """Creates a working directory for use while building"""
        ts = time.time()
        ts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S_')
        self.temp_dir = tempfile.mkdtemp(prefix='kolla-' + ts)
        self.working_dir = os.path.join(self.temp_dir, 'docker')
        shutil.copytree(self.images_dir, self.working_dir)
        LOG.debug('Created working dir: %s', self.working_dir)

    def set_time(self):
        for root, dirs, files in os.walk(self.working_dir):
            for file_ in files:
                os.utime(os.path.join(root, file_), (0, 0))
            for dir_ in dirs:
                os.utime(os.path.join(root, dir_), (0, 0))
        LOG.debug('Set atime and mtime to 0 for all content in working dir')

    def create_dockerfiles(self):
        for path in self.docker_build_paths:
            template_name = "Dockerfile.j2"
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
            template = env.get_template(template_name)
            values = {'base_distro': self.base,
                      'base_distro_tag': self.base_tag,
                      'install_metatype': self.install_metatype,
                      'image_prefix': self.image_prefix,
                      'install_type': self.install_type,
                      'namespace': self.namespace,
                      'tag': self.tag,
                      'maintainer': self.maintainer,
                      'kolla_version': get_kolla_version(),
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

        if self.conf.profile:
            for profile in self.conf.profile:
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
            for name, status in six.iteritems(self.image_statuses_bad):
                LOG.error('%s\r\t\t\t Failed with status: %s', name, status)

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
            if section not in self.conf.list_all_sections():
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
                self.conf.register_opts([
                    cfg.StrOpt('type'),
                    cfg.StrOpt('location'),
                    cfg.StrOpt('reference')
                ], image['name'])
                image['source'] = process_source_installation(image,
                                                              image['name'])
                for plugin in [match.group(0) for match in
                               (re.search('{}-plugin-.+'.format(image['name']),
                                          section) for section in
                               self.conf.list_all_sections()) if match]:
                    image['plugins'].append(
                        process_source_installation(image, plugin))

            self.images.append(image)

    def find_parents(self):
        """Associate all images with parents and children"""
        sort_images = dict()

        for image in self.images:
            sort_images[image['fullname']] = image

        for parent_name, parent in six.iteritems(sort_images):
            for image in sort_images.values():
                if image['parent_name'] == parent_name:
                    parent['children'].append(image)
                    image['parent'] = parent

    def build_queue(self):
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
                queue.put(image)
                LOG.debug('%s:Added image to queue', image['name'])

        return queue


def get_conf():
    conf = cfg.ConfigOpts()

    _kolla_profile_opts = [
        cfg.ListOpt('infra',
                    default=['ceph', 'data', 'mariadb', 'haproxy',
                             'keepalived', 'kolla-ansible', 'memcached',
                             'mongodb', 'openvswitch', 'rabbitmq', 'rsyslog']),
        cfg.ListOpt('main',
                    default=['cinder', 'ceilometer', 'glance', 'heat',
                             'horizon', 'keystone', 'neutron', 'nova',
                             'swift']),
        cfg.ListOpt('aux',
                    default=['aodh', 'designate', 'gnocchi', 'ironic',
                             'magnum', 'mistral', 'trove,' 'zaqar']),
        cfg.ListOpt('default',
                    default=['data', 'kolla-ansible', 'glance', 'haproxy',
                             'heat', 'horizon', 'keepalived', 'keystone',
                             'memcached', 'mariadb', 'neutron', 'nova',
                             'openvswitch', 'rabbitmq', 'rsyslog']),
        cfg.ListOpt('gate',
                    default=['ceph', 'cinder', 'data', 'dind', 'glance',
                             'haproxy', 'heat', 'horizon', 'keepalived',
                             'keystone', 'kolla-ansible', 'mariadb',
                             'memcached', 'neutron', 'nova', 'openvswitch',
                             'rabbitmq', 'rsyslog'])
    ]

    _kolla_cli_opts = [
        cfg.StrOpt('base', short='b', default='centos',
                   deprecated_group='kolla-build',
                   help='The base distro to use when building'),
        cfg.StrOpt('base_tag', default='latest',
                   deprecated_group='kolla-build',
                   help='The base distro image tag'),
        cfg.BoolOpt('debug', short='d', default=False,
                    deprecated_group='kolla-build',
                    help='Turn on debugging log level'),
        cfg.StrOpt('include-header', short='i',
                   deprecated_group='kolla-build',
                   help=('Path to custom file to be added at '
                         'beginning of base Dockerfile')),
        cfg.StrOpt('include-footer', short='I',
                   deprecated_group='kolla-build',
                   help=('Path to custom file to be added at '
                         'end of Dockerfiles for final images')),
        cfg.BoolOpt('keep', default=False,
                    deprecated_group='kolla-build',
                    help='Keep failed intermediate containers'),
        cfg.StrOpt('namespace', short='n', default='kollaglue',
                   deprecated_group='kolla-build',
                   help='The Docker namespace name'),
        cfg.BoolOpt('cache', default=True,
                    help='Use the Docker cache when building',
                    ),
        cfg.BoolOpt('no-cache', default=False,
                    help='Do not use the Docker cache when building',
                    deprecated_for_removal=True),
        cfg.MultiOpt('profile', types.String(), short='p',
                     deprecated_group='kolla-build',
                     help=('Build a pre-defined set of images, see [profiles]'
                           ' section in {}. The default profiles are:'
                           ' {}'.format(
                               find_config_file('kolla-build.conf'),
                               ', '.join(
                                   [opt.name for opt in _kolla_profile_opts])
                           ))),
        cfg.BoolOpt('push', default=False,
                    deprecated_group='kolla-build',
                    help='Push images after building'),
        cfg.IntOpt('push-threads', default=1, min=1,
                   deprecated_group='kolla-build',
                   help=('The number of threads to user while pushing'
                         ' Images. Note: Docker can not handle threading'
                         ' push properly.')),
        cfg.IntOpt('retries', short='r', default=3, min=0,
                   deprecated_group='kolla-build',
                   help='The number of times to retry while building'),
        cfg.MultiOpt('regex', types.String(), positional=True,
                     help=('Build only images matching regex and its'
                           ' dependencies')),
        cfg.StrOpt('registry', deprecated_group='kolla-build',
                   help=('The docker registry host. The default registry host'
                         ' is Docker Hub')),
        cfg.StrOpt('type', short='t', default='binary',
                   choices=INSTALL_TYPE_CHOICES,
                   dest='install_type', deprecated_group='kolla-build',
                   help=('The method of the Openstack install. The valid'
                         ' types are: {}'.format(
                             ', '.join(INSTALL_TYPE_CHOICES)))),
        cfg.IntOpt('threads', short='T', default=8, min=1,
                   deprecated_group='kolla-build',
                   help=('The number of threads to use while building.'
                         ' (Note: setting to one will allow real time'
                         ' logging.)')),
        cfg.StrOpt('tag', default=get_kolla_version(),
                   deprecated_group='kolla-build',
                   help='The Docker tag'),
        cfg.BoolOpt('template-only', default=False,
                    deprecated_group='kolla-build',
                    help=("Don't build images. Generate Dockerfile only")),
    ]

    _kolla_base_opts = [
        cfg.StrOpt('maintainer', deprecated_group='kolla-build',
                   default='Kolla Project (https://launchpad.net/kolla)',
                   help='The MAINTAINER field'),
        cfg.ListOpt('rpm_setup_config', default=[DELOREAN, DELOREAN_DEPS],
                    deprecated_group='kolla-build',
                    help=('Comma separated list of .rpm or .repo file(s)'
                          'or URL(s) to install before building containers'))
    ]
    conf.register_cli_opts(_kolla_cli_opts)
    conf.register_opts(_kolla_profile_opts, group='profiles')
    conf.register_opts(_kolla_base_opts)
    conf(sys.argv[1:],
         default_config_files=[find_config_file('kolla-build.conf')])
    return conf


def main():
    conf = get_conf()

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

    queue = kolla.build_queue()
    push_queue = six.moves.queue.Queue()

    for x in six.moves.xrange(conf.threads):
        worker = WorkerThread(queue, push_queue, conf)
        worker.setDaemon(True)
        worker.start()

    for x in six.moves.xrange(conf.push_threads):
        push_thread = PushThread(conf, push_queue)
        push_thread.start()

    # block until queue is empty
    queue.join()
    push_queue.join()

    kolla.summary()
    kolla.cleanup()

    return kolla.get_image_statuses()


if __name__ == '__main__':
    main()
