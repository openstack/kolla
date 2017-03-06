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

import contextlib
import datetime
import errno
import json
import logging
import os
import pprint
import re
import requests
import shutil
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

# NOTE(SamYaple): Update the search path to prefer PROJECT_ROOT as the source
#                 of packages to import if we are using local tools instead of
#                 pip installed kolla tools
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kolla.common import config as common_config
from kolla.common import task
from kolla import exception
from kolla.template import filters as jinja_filters
from kolla.template import methods as jinja_methods
from kolla import version


def make_a_logger(conf=None, image_name=None):
    if image_name:
        log = logging.getLogger(".".join([__name__, image_name]))
    else:
        log = logging.getLogger(__name__)
    if not log.handlers:
        if conf is None or not conf.logs_dir or not image_name:
            handler = logging.StreamHandler(sys.stdout)
            log.propagate = False
        else:
            filename = os.path.join(conf.logs_dir, "%s.log" % image_name)
            handler = logging.FileHandler(filename, delay=True)
        handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        log.addHandler(handler)
    if conf is not None and conf.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    return log


LOG = make_a_logger()

# Image status constants.
#
# TODO(harlowja): use enum lib in the future??
STATUS_CONNECTION_ERROR = 'connection_error'
STATUS_PUSH_ERROR = 'push_error'
STATUS_ERROR = 'error'
STATUS_PARENT_ERROR = 'parent_error'
STATUS_BUILT = 'built'
STATUS_BUILDING = 'building'
STATUS_UNMATCHED = 'unmatched'
STATUS_MATCHED = 'matched'
STATUS_UNPROCESSED = 'unprocessed'

# All error status constants.
STATUS_ERRORS = (STATUS_CONNECTION_ERROR, STATUS_PUSH_ERROR,
                 STATUS_ERROR, STATUS_PARENT_ERROR)


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
        self._dc = docker.Client(version='auto', **docker_kwargs)
        return self._dc


class Image(object):
    def __init__(self, name, canonical_name, path, parent_name='',
                 status=STATUS_UNPROCESSED, parent=None,
                 source=None, logger=None):
        self.name = name
        self.canonical_name = canonical_name
        self.path = path
        self.status = status
        self.parent = parent
        self.source = source
        self.parent_name = parent_name
        if logger is None:
            logger = make_a_logger(image_name=name)
        self.logger = logger
        self.children = []
        self.plugins = []

    def copy(self):
        c = Image(self.name, self.canonical_name, self.path,
                  logger=self.logger, parent_name=self.parent_name,
                  status=self.status, parent=self.parent)
        if self.source:
            c.source = self.source.copy()
        if self.children:
            c.children = list(self.children)
        if self.plugins:
            c.plugins = list(self.plugins)
        return c

    def __repr__(self):
        return ("Image(%s, %s, %s, parent_name=%s,"
                " status=%s, parent=%s, source=%s)") % (
            self.name, self.canonical_name, self.path,
            self.parent_name, self.status, self.parent, self.source)


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
            image.status = STATUS_CONNECTION_ERROR
        except Exception:
            self.logger.exception('Unknown error when pushing')
            image.status = STATUS_PUSH_ERROR
        finally:
            if (image.status not in STATUS_ERRORS
                    and image.status != STATUS_UNPROCESSED):
                self.logger.info('Pushed successfully')
                self.success = True
            else:
                self.success = False

    def push_image(self, image):
        for response in self.dc.push(image.canonical_name,
                                     stream=True,
                                     insecure_registry=True):
            stream = json.loads(response)
            if 'stream' in stream:
                self.logger.info(stream['stream'])
            elif 'errorDetail' in stream:
                image.status = STATUS_ERROR
                self.logger.error(stream['errorDetail']['message'])


class BuildTask(DockerTask):
    """Task that builds out an image."""

    def __init__(self, conf, image, push_queue):
        super(BuildTask, self).__init__()
        self.conf = conf
        self.image = image
        self.push_queue = push_queue
        self.nocache = not conf.cache
        self.forcerm = not conf.keep
        self.logger = image.logger

    @property
    def name(self):
        return 'BuildTask(%s)' % self.image.name

    def run(self):
        self.builder(self.image)
        if self.image.status == STATUS_BUILT:
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
                if image.status == STATUS_UNMATCHED:
                    continue
                followups.append(BuildTask(self.conf, image, self.push_queue))
        return followups

    def process_source(self, image, source):
        dest_archive = os.path.join(image.path, source['name'] + '-archive')

        if source.get('type') == 'url':
            self.logger.debug("Getting archive from %s", source['source'])
            try:
                r = requests.get(source['source'], timeout=self.conf.timeout)
            except requests_exc.Timeout:
                self.logger.exception(
                    'Request timed out while getting archive from %s',
                    source['source'])
                image.status = STATUS_ERROR
                return

            if r.status_code == 200:
                with open(dest_archive, 'wb') as f:
                    f.write(r.content)
            else:
                self.logger.error(
                    'Failed to download archive: status_code %s',
                    r.status_code)
                image.status = STATUS_ERROR
                return

        elif source.get('type') == 'git':
            clone_dir = '{}-{}'.format(dest_archive,
                                       source['reference'].replace('/', '-'))
            try:
                self.logger.debug("Cloning from %s", source['source'])
                git.Git().clone(source['source'], clone_dir)
                git.Git(clone_dir).checkout(source['reference'])
                reference_sha = git.Git(clone_dir).rev_parse('HEAD')
                self.logger.debug("Git checkout by reference %s (%s)",
                                  source['reference'], reference_sha)
            except Exception as e:
                self.logger.error("Failed to get source from git", image.name)
                self.logger.error("Error: %s", e)
                # clean-up clone folder to retry
                shutil.rmtree(clone_dir)
                image.status = STATUS_ERROR
                return

            with tarfile.open(dest_archive, 'w') as tar:
                tar.add(clone_dir, arcname=os.path.basename(clone_dir))

        elif source.get('type') == 'local':
            self.logger.debug("Getting local archive from %s",
                              source['source'])
            if os.path.isdir(source['source']):
                with tarfile.open(dest_archive, 'w') as tar:
                    tar.add(source['source'],
                            arcname=os.path.basename(source['source']))
            else:
                shutil.copyfile(source['source'], dest_archive)

        else:
            self.logger.error("Wrong source type '%s'", source.get('type'))
            image.status = STATUS_ERROR
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
        self.logger.debug('Processing')
        if image.status == STATUS_UNMATCHED:
            return

        if (image.parent is not None and
                image.parent.status in STATUS_ERRORS):
            self.logger.error('Parent image error\'d with message "%s"',
                              image.parent.status)
            image.status = STATUS_PARENT_ERROR
            return

        image.status = STATUS_BUILDING
        self.logger.info('Building')

        if image.source and 'source' in image.source:
            self.process_source(image, image.source)
            if image.status in STATUS_ERRORS:
                return

        plugin_archives = list()
        plugins_path = os.path.join(image.path, 'plugins')
        for plugin in image.plugins:
            archive_path = self.process_source(image, plugin)
            if image.status in STATUS_ERRORS:
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
                    self.logger.info('Directory %s already exist. Skipping.',
                                     plugins_path)
                else:
                    self.logger.error('Failed to create directory %s: %s',
                                      plugins_path, e)
                    image.status = STATUS_CONNECTION_ERROR
                    return
        with tarfile.open(os.path.join(image.path, 'plugins-archive'),
                          'w') as tar:
            tar.add(plugins_path, arcname='plugins')

        # Pull the latest image for the base distro only
        pull = self.conf.pull if image.parent is None else False

        buildargs = self.update_buildargs()
        try:
            for response in self.dc.build(path=image.path,
                                          tag=image.canonical_name,
                                          nocache=not self.conf.cache,
                                          rm=True,
                                          pull=pull,
                                          forcerm=self.forcerm,
                                          buildargs=buildargs):
                stream = json.loads(response.decode('utf-8'))
                if 'stream' in stream:
                    for line in stream['stream'].split('\n'):
                        if line:
                            self.logger.info('%s', line)
                if 'errorDetail' in stream:
                    image.status = STATUS_ERROR
                    self.logger.error('Error\'d with the following message')
                    for line in stream['errorDetail']['message'].split('\n'):
                        if line:
                            self.logger.error('%s', line)
                    return
        except docker.errors.DockerException:
            image.status = STATUS_ERROR
            self.logger.exception('Unknown docker error when building')
        except Exception:
            image.status = STATUS_ERROR
            self.logger.exception('Unknown error when building')
        else:
            image.status = STATUS_BUILT
            self.logger.info('Built')


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
                for attempt in six.moves.range(self.conf.retries + 1):
                    if self.should_stop:
                        break
                    if attempt > 0:
                        LOG.info("Attempting to run task %s for the %s time",
                                 task.name, attempt + 1)
                    else:
                        LOG.info("Attempting to run task %s for the first"
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
                if task.success and not self.should_stop:
                    for next_task in task.followups:
                        LOG.info('Added next task %s to queue',
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
        rpm_setup_config = ([repo_file for repo_file in
                             conf.rpm_setup_config if repo_file is not None])
        self.rpm_setup = self.build_rpm_setup(rpm_setup_config)

        rh_base = ['centos', 'oraclelinux', 'rhel']
        rh_type = ['source', 'binary', 'rdo', 'rhos']
        deb_base = ['ubuntu', 'debian']
        deb_type = ['source', 'binary']

        if not ((self.base in rh_base and self.install_type in rh_type) or
                (self.base in deb_base and self.install_type in deb_type)):
            raise exception.KollaMismatchBaseTypeException(
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
            raise exception.KollaUnknownBuildTypeException(
                'Unknown install type'
            )

        self.image_prefix = self.base + '-' + self.install_type + '-'

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
            raise exception.KollaDirNotFoundException('Image dir can not '
                                                      'be found')

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
                    cmd = "RUN curl -L {} -o /etc/yum.repos.d/{}".format(
                        config, name)
                else:
                    # Copy .repo file from filesystem
                    cmd = "COPY {} /etc/yum.repos.d/".format(config)
            else:
                raise exception.KollaRpmSetupUnknownConfig(
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

    def _get_filters(self):
        filters = {
            'customizable': jinja_filters.customizable,
        }
        return filters

    def _get_methods(self):
        """Mapping of available Jinja methods

        return a dictionary that maps available function names and their
        corresponding python methods to make them available in jinja templates
        """

        return {
            'debian_package_install': jinja_methods.debian_package_install,
        }

    def get_users(self):
        all_sections = (set(six.iterkeys(self.conf._groups)) |
                        set(self.conf.list_all_sections()))
        ret = dict()
        for section in all_sections:
            match = re.search('^.*-user$', section)
            if match:
                user = self.conf[match.group(0)]
                ret[match.group(0)[:-5]] = {
                    'uid': user.uid,
                    'gid': user.gid,
                }
        return ret

    def create_dockerfiles(self):
        kolla_version = version.version_info.cached_version_string()
        supported_distro_release = common_config.DISTRO_RELEASE.get(
            self.base)
        for path in self.docker_build_paths:
            template_name = "Dockerfile.j2"
            image_name = path.split("/")[-1]
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
                      'image_name': image_name,
                      'users': self.get_users(),
                      'rpm_setup': self.rpm_setup}
            env = jinja2.Environment(  # nosec: not used to render HTML
                loader=jinja2.FileSystemLoader(self.working_dir))
            env.filters.update(self._get_filters())
            env.globals.update(self._get_methods())
            tpl_path = os.path.join(
                os.path.relpath(path, self.working_dir),
                template_name)

            template = env.get_template(tpl_path)
            if self.conf.template_override:
                tpl_dict = self._merge_overrides(self.conf.template_override)
                template_name = os.path.basename(tpl_dict.keys()[0])
                values['parent_template'] = template
                env = jinja2.Environment(  # nosec: not used to render HTML
                    loader=jinja2.DictLoader(tpl_dict))
                env.filters.update(self._get_filters())
                env.globals.update(self._get_methods())
                template = env.get_template(template_name)
            content = template.render(values)
            content_path = os.path.join(path, 'Dockerfile')
            with open(content_path, 'w') as f:
                LOG.debug("Rendered %s into:", tpl_path)
                LOG.debug(content)
                f.write(content)
                LOG.debug("Wrote it to %s", content_path)

    def _merge_overrides(self, overrides):
        tpl_name = os.path.basename(overrides[0])
        with open(overrides[0], 'r') as f:
            tpl_content = f.read()
        for override in overrides[1:]:
            with open(override, 'r') as f:
                cont = f.read()
            # Remove extends header
            cont = re.sub(r'.*\{\%.*extends.*\n', '', cont)
            tpl_content += cont
        return {tpl_name: tpl_content}

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
                if image.status == STATUS_MATCHED:
                    continue
                if re.search(patterns, image.name):
                    image.status = STATUS_MATCHED
                    while (image.parent is not None and
                           image.parent.status != STATUS_MATCHED):
                        image = image.parent
                        image.status = STATUS_MATCHED
                        LOG.debug('Image %s matched regex', image.name)
                else:
                    image.status = STATUS_UNMATCHED
        else:
            for image in self.images:
                image.status = STATUS_MATCHED

    def summary(self):
        """Walk the dictionary of images statuses and print results"""
        # For debug we print the logs again if the image error'd. This is to
        # help us debug and it will be extra helpful in the gate.
        for image in self.images:
            if image.status in STATUS_ERRORS:
                LOG.debug("Image %s failed", image.name)

        self.get_image_statuses()
        results = {
            'built': [],
            'failed': [],
            'not_matched': [],
        }

        if self.image_statuses_good:
            LOG.info("=========================")
            LOG.info("Successfully built images")
            LOG.info("=========================")
            for name in self.image_statuses_good.keys():
                LOG.info(name)
                results['built'].append({
                    'name': name,
                })

        if self.image_statuses_bad:
            LOG.info("===========================")
            LOG.info("Images that failed to build")
            LOG.info("===========================")
            for name, status in self.image_statuses_bad.items():
                LOG.error('%s Failed with status: %s', name, status)
                results['failed'].append({
                    'name': name,
                    'status': status,
                })

        if self.image_statuses_unmatched:
            LOG.debug("=====================================")
            LOG.debug("Images not matched for build by regex")
            LOG.debug("=====================================")
            for name in self.image_statuses_unmatched.keys():
                LOG.debug(name)
                results['not_matched'].append({
                    'name': name,
                })

        return results

    def get_image_statuses(self):
        if any([self.image_statuses_bad,
                self.image_statuses_good,
                self.image_statuses_unmatched]):
            return (self.image_statuses_bad,
                    self.image_statuses_good,
                    self.image_statuses_unmatched)
        for image in self.images:
            if image.status == STATUS_BUILT:
                self.image_statuses_good[image.name] = image.status
            elif image.status == STATUS_UNMATCHED:
                self.image_statuses_unmatched[image.name] = image.status
            else:
                self.image_statuses_bad[image.name] = image.status
        return (self.image_statuses_bad,
                self.image_statuses_good,
                self.image_statuses_unmatched)

    def build_image_list(self):
        def process_source_installation(image, section):
            installation = dict()
            # NOTE(jeffrey4l): source is not needed when the type is None
            if self.conf._get('type', self.conf._get_group(section)) is None:
                if image.parent_name is None:
                    LOG.debug('No source location found in section %s',
                              section)
            else:
                installation['type'] = self.conf[section]['type']
                installation['source'] = self.conf[section]['location']
                installation['name'] = section
                if installation['type'] == 'git':
                    installation['reference'] = self.conf[section]['reference']
            return installation

        all_sections = (set(six.iterkeys(self.conf._groups)) |
                        set(self.conf.list_all_sections()))

        for path in self.docker_build_paths:
            # Reading parent image name
            with open(os.path.join(path, 'Dockerfile')) as f:
                content = f.read()

            image_name = os.path.basename(path)
            canonical_name = (self.namespace + '/' + self.image_prefix +
                              image_name + ':' + self.tag)
            parent_search_pattern = re.compile(r'^FROM.*$', re.MULTILINE)
            match = re.search(parent_search_pattern, content)
            if match:
                parent_name = match.group(0).split(' ')[1]
            else:
                parent_name = ''
            del match
            image = Image(image_name, canonical_name, path,
                          parent_name=parent_name,
                          logger=make_a_logger(self.conf, image_name))

            if self.install_type == 'source':
                # NOTE(jeffrey4l): register the opts if the section didn't
                # register in the kolla/common/config.py file
                if image.name not in self.conf._groups:
                    self.conf.register_opts(common_config.get_source_opts(),
                                            image.name)
                image.source = process_source_installation(image, image.name)
                for plugin in [match.group(0) for match in
                               (re.search('^{}-plugin-.+'.format(image.name),
                                          section) for section in
                                all_sections) if match]:
                    try:
                        self.conf.register_opts(
                            common_config.get_source_opts(),
                            plugin
                        )
                    except cfg.DuplicateOptError:
                        LOG.debug('Plugin %s already registered in config',
                                  plugin)
                    image.plugins.append(
                        process_source_installation(image, plugin))

            self.images.append(image)

    def save_dependency(self, to_file):
        try:
            import graphviz
        except ImportError:
            LOG.error('"graphviz" is required for save dependency')
            raise
        dot = graphviz.Digraph(comment='Docker Images Dependency')
        dot.body.extend(['rankdir=LR'])
        for image in self.images:
            if image.status not in [STATUS_MATCHED]:
                continue
            dot.node(image.name)
            if image.parent is not None:
                dot.edge(image.parent.name, image.name)

        with open(to_file, 'w') as f:
            f.write(dot.source)

    def list_images(self):
        for count, image in enumerate([
            image for image in self.images if image.status == STATUS_MATCHED
        ]):
            print(count + 1, ':', image.name)

    def list_dependencies(self):
        match = False
        for image in self.images:
            if image.status in [STATUS_MATCHED]:
                match = True
            if image.parent is None:
                base = image
        if not match:
            print('Nothing matched!')
            return

        def list_children(images, ancestry):
            children = six.next(iter(ancestry.values()))
            for image in images:
                if image.status not in [STATUS_MATCHED]:
                    continue
                if not image.children:
                    children.append(image.name)
                else:
                    newparent = {image.name: []}
                    children.append(newparent)
                    list_children(image.children, newparent)

        ancestry = {base.name: []}
        list_children(base.children, ancestry)
        pprint.pprint(ancestry)

    def find_parents(self):
        """Associate all images with parents and children"""
        sort_images = dict()

        for image in self.images:
            sort_images[image.canonical_name] = image

        for parent_name, parent in sort_images.items():
            for image in sort_images.values():
                if image.parent_name == parent_name:
                    parent.children.append(image)
                    image.parent = parent

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
            if image.status == STATUS_UNMATCHED:
                # Don't bother queuing up build tasks for things that
                # were not matched in the first place... (not worth the
                # effort to run them, if they won't be used anyway).
                continue
            if image.parent is None:
                queue.put(BuildTask(self.conf, image, push_queue))
                LOG.info('Added image %s to queue', image.name)

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
        kolla.build_image_list()
        kolla.find_parents()
        kolla.filter_images()
        kolla.save_dependency(conf.save_dependency)
        LOG.info('Docker images dependency are saved in %s',
                 conf.save_dependency)
        return
    if conf.list_images:
        kolla.build_image_list()
        kolla.find_parents()
        kolla.filter_images()
        kolla.list_images()
        return
    if conf.list_dependencies:
        kolla.build_image_list()
        kolla.find_parents()
        kolla.filter_images()
        kolla.list_dependencies()
        return

    push_queue = six.moves.queue.Queue()
    queue = kolla.build_queue(push_queue)
    workers = []

    with join_many(workers):
        try:
            for x in six.moves.range(conf.threads):
                worker = WorkerThread(conf, queue)
                worker.setDaemon(True)
                worker.start()
                workers.append(worker)

            for x in six.moves.range(conf.push_threads):
                worker = WorkerThread(conf, push_queue)
                worker.setDaemon(True)
                worker.start()
                workers.append(worker)

            # sleep until queue is empty
            while queue.unfinished_tasks or push_queue.unfinished_tasks:
                time.sleep(3)

            # ensure all threads exited happily
            push_queue.put(WorkerThread.tombstone)
            queue.put(WorkerThread.tombstone)
        except KeyboardInterrupt:
            for w in workers:
                w.should_stop = True
            push_queue.put(WorkerThread.tombstone)
            queue.put(WorkerThread.tombstone)
            raise

    results = kolla.summary()
    kolla.cleanup()
    if conf.format == 'json':
        print(json.dumps(results))
    return kolla.get_image_statuses()
