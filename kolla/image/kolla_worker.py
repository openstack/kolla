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
import json
import os
import queue
import re
import shutil
import sys
import tempfile
import time

import jinja2
from kolla.common import config as common_config
from kolla.common import utils
from kolla.engine_adapter import engine
from kolla import exception
from kolla.image.tasks import BuildTask
from kolla.image.unbuildable import UNBUILDABLE_IMAGES
from kolla.image.utils import LOG
from kolla.image.utils import Status
from kolla.image.utils import STATUS_ERRORS
from kolla.template import filters as jinja_filters
from kolla.template import methods as jinja_methods
from kolla import version
from oslo_config import cfg

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../..'))


class Image(object):
    def __init__(self, name, canonical_name, path, parent_name='',
                 status=Status.UNPROCESSED, parent=None,
                 source=None, logger=None, engine_client=None):
        self.name = name
        self.canonical_name = canonical_name
        self.path = path
        self.status = status
        self.parent = parent
        self.source = source
        self.parent_name = parent_name
        if logger is None:
            logger = utils.make_a_logger(image_name=name)
        self.logger = logger
        self.children = []
        self.plugins = []
        self.additions = []
        self.engine_client = engine_client

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
        if self.additions:
            c.additions = list(self.additions)
        return c

    def in_engine_cache(self):
        return len(self.engine_client.images.list(
            name=self.canonical_name)) >= 1

    def __repr__(self):
        return ("Image(%s, %s, %s, parent_name=%s,"
                " status=%s, parent=%s, source=%s)") % (
            self.name, self.canonical_name, self.path,
            self.parent_name, self.status, self.parent, self.source)


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
        self.use_dumb_init = conf.use_dumb_init
        self.base_tag = conf.base_tag
        self.tag = conf.tag
        self.repos_yaml = conf.repos_yaml
        self.base_arch = conf.base_arch
        self.debian_arch = self.base_arch
        if self.base_arch == 'aarch64':
            self.debian_arch = 'arm64'
        elif self.base_arch == 'x86_64':
            self.debian_arch = 'amd64'
        self.images = list()
        self.openstack_release = conf.openstack_release
        self.openstack_branch = conf.openstack_branch
        self.openstack_branch_slashed = conf.openstack_branch_slashed
        self.docker_healthchecks = conf.docker_healthchecks
        rpm_setup_config = ([repo_file for repo_file in
                             conf.rpm_setup_config if repo_file is not None])
        self.rpm_setup = self.build_rpm_setup(rpm_setup_config)

        if self.base in ['centos', 'rocky']:
            self.distro_package_manager = 'dnf'
            self.base_package_type = 'rpm'
        elif self.base in ['debian']:
            self.distro_package_manager = 'apt'
            self.base_package_type = 'deb'
        elif self.base in ['ubuntu']:
            self.distro_package_manager = 'apt'
            self.base_package_type = 'deb'

        if self.conf.distro_package_manager is not None:
            self.distro_package_manager = self.conf.distro_package_manager

        if self.conf.base_package_type:
            self.base_package_type = self.conf.base_package_type

        self.clean_package_cache = self.conf.clean_package_cache

        self.image_prefix = self.conf.image_name_prefix

        self.regex = conf.regex
        self.image_statuses_bad = dict()
        self.image_statuses_good = dict()
        self.image_statuses_unmatched = dict()
        self.image_statuses_skipped = dict()
        self.image_statuses_unbuildable = dict()
        self.image_statuses_allowed_to_fail = dict()
        self.maintainer = conf.maintainer

        try:
            self.engine_client = engine.getEngineClient(self.conf)
        except engine.getEngineException(self.conf) as e:
            self.engine_client = None
            if not (conf.template_only or
                    conf.save_dependency or
                    conf.list_images or
                    conf.list_dependencies):
                LOG.error("Unable to connect to container engine daemon, "
                          "exiting")
                LOG.info("Exception caught: {0}".format(e))
                sys.exit(1)

    def _get_images_dir(self):
        possible_paths = (
            PROJECT_ROOT,
            os.path.join(sys.prefix, 'share/kolla'),
            os.path.join(sys.prefix, 'local/share/kolla'),
            os.path.join(os.getenv('HOME', ''), '.local/share/kolla'),
            # NOTE(zioproto): When Kolla is used within a snap, the env var
            #                 $SNAP is the directory where the snap is mounted.
            #                 https://github.com/zioproto/snap-kolla
            #                 More info in snap packages https://snapcraft.io
            os.path.join(os.environ.get('SNAP', ''), 'share/kolla'))

        for path in possible_paths:
            image_path = os.path.join(path, 'docker')
            # NOTE(SamYaple): We explicitly check for the base folder to ensure
            #                 this is the correct path
            # TODO(SamYaple): Improve this to make this safer
            if os.path.exists(os.path.join(image_path, 'base')):
                LOG.info('Found the container image folder at %s', image_path)
                return image_path
        else:
            raise exception.KollaDirNotFoundException('Image dir can not '
                                                      'be found')

    def build_rpm_setup(self, rpm_setup_config):
        """Generates a list of engine commands based on provided configuration

        :param rpm_setup_config: A list of .rpm or .repo paths or URLs
                                 (can be empty)
        :return: A list of engine commands
        """
        rpm_setup = list()

        for config in rpm_setup_config:
            if config.endswith('.rpm'):
                # RPM files can be installed with dnf from file path or url
                cmd = "RUN dnf -y install {}".format(config)
            elif config.endswith('.repo'):
                if config.startswith('http'):
                    # Curl http://url/etc.repo to /etc/yum.repos.d/etc.repo
                    name = config.split('/')[-1]
                    cmd = "RUN curl -L {} -o /etc/yum.repos.d/{}".format(
                        config, name)
                else:
                    # Copy .repo file from filesystem
                    cmd = "COPY {} /etc/yum.repos.d/".format(config)
            elif not config:
                cmd = ''
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

    def copy_dir(self, src, dest):
        shutil.copytree(src, dest, dirs_exist_ok=True)

    def setup_working_dir(self):
        """Creates a working directory for use while building."""
        if self.conf.work_dir:
            self.working_dir = os.path.join(self.conf.work_dir, 'docker')
        else:
            ts = time.time()
            ts = datetime.datetime.fromtimestamp(ts).strftime(
                '%Y-%m-%d_%H-%M-%S_')
            self.temp_dir = tempfile.mkdtemp(prefix='kolla-' + ts)
            self.working_dir = os.path.join(self.temp_dir, 'docker')
        self.copy_dir(self.images_dir, self.working_dir)
        if self.conf.docker_dir:
            for dir in self.conf.docker_dir:
                self.copy_dir(dir, self.working_dir)
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
        """Mapping of available Jinja methods.

        return a dictionary that maps available function names and their
        corresponding python methods to make them available in jinja templates
        """

        return {
            'debian_package_install': jinja_methods.debian_package_install,
            'handle_repos': jinja_methods.handle_repos,
        }

    def get_users(self):
        all_sections = (set(self.conf._groups.keys()) |
                        set(self.conf.list_all_sections()))
        ret = dict()
        for section in all_sections:
            match = re.search('^.*-user$', section)
            if match:
                user = self.conf[match.group(0)]
                ret[match.group(0)[:-5]] = {
                    'uid': user.uid,
                    'gid': user.gid,
                    'group': user.group,
                }
        return ret

    def create_dockerfiles(self):
        kolla_version = version.git_info if len(version.git_info) != 0 else \
            version.version_info.cached_version_string()
        supported_distro_name = common_config.DISTRO_PRETTY_NAME.get(
            self.base)
        for path in self.docker_build_paths:
            template_name = "Dockerfile.j2"
            image_name = path.split("/")[-1]
            ts = time.time()
            build_date = datetime.datetime.fromtimestamp(ts).strftime(
                '%Y%m%d')
            values = {'base_distro': self.base,
                      'base_image': self.conf.base_image,
                      'base_distro_tag': self.base_tag,
                      'base_arch': self.base_arch,
                      'repos_yaml': self.repos_yaml,
                      'use_dumb_init': self.use_dumb_init,
                      'base_package_type': self.base_package_type,
                      'debian_arch': self.debian_arch,
                      'docker_healthchecks': self.docker_healthchecks,
                      'supported_distro_name': supported_distro_name,
                      'image_prefix': self.image_prefix,
                      'namespace': self.namespace,
                      'openstack_release': self.openstack_release,
                      'openstack_branch': self.openstack_branch,
                      'openstack_branch_slashed':
                          self.openstack_branch_slashed,
                      'tag': self.tag,
                      'maintainer': self.maintainer,
                      'kolla_version': kolla_version,
                      'image_name': image_name,
                      'users': self.get_users(),
                      'distro_package_manager': self.distro_package_manager,
                      'rpm_setup': self.rpm_setup,
                      'build_date': build_date,
                      'clean_package_cache': self.clean_package_cache}
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
                template_name = os.path.basename(list(tpl_dict.keys())[0])
                values['parent_template'] = template
                env = jinja2.Environment(  # nosec: not used to render HTML
                    loader=jinja2.DictLoader(tpl_dict))
                env.filters.update(self._get_filters())
                env.globals.update(self._get_methods())
                template = env.get_template(template_name)
            content = template.render(values, env=os.environ)
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
        """Recursive search for Dockerfiles in the working directory."""
        self.docker_build_paths = list()
        path = self.working_dir
        filename = 'Dockerfile.j2'

        for root, dirs, names in os.walk(path):
            if filename in names:
                self.docker_build_paths.append(root)
                LOG.debug('Found %s', root.split(self.working_dir)[1])

        LOG.debug('Found %d Dockerfiles', len(self.docker_build_paths))

    def cleanup(self):
        """Remove temp files."""
        if not self.conf.work_dir:
            shutil.rmtree(self.temp_dir)

    def filter_images(self):
        """Filter which images to build."""
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

        # mark unbuildable images and their children
        base = self.base

        tag_element = r'(%s|%s)' % (base, self.base_arch)
        tag_re = re.compile(r'^%s(\+%s)*$' % (tag_element, tag_element))
        unbuildable_images = set()

        if not self.conf.enable_unbuildable:
            for set_tag in UNBUILDABLE_IMAGES:
                if tag_re.match(set_tag):
                    unbuildable_images.update(UNBUILDABLE_IMAGES[set_tag])

        if unbuildable_images:
            for image in self.images:
                if image.name in unbuildable_images:
                    image.status = Status.UNBUILDABLE
                else:
                    # let's check ancestors
                    # if any of them is unbuildable then we mark it
                    # and then mark image
                    build_image = True
                    ancestor_image = image
                    while (ancestor_image.parent is not None):
                        ancestor_image = ancestor_image.parent
                        if ancestor_image.name in unbuildable_images or \
                           ancestor_image.status == Status.UNBUILDABLE:
                            build_image = False
                            ancestor_image.status = Status.UNBUILDABLE
                            break
                    if not build_image:
                        image.status = Status.UNBUILDABLE

        # When we want to build a subset of images then filter_ part kicks in.
        # Otherwise we just mark everything buildable as matched for build.

        # First, determine which buildable images match.
        if filter_:
            patterns = re.compile(r"|".join(filter_).join('()'))
            for image in self.images:
                # as we now list not buildable/skipped images we need to
                # process them otherwise list will contain also not requested
                # entries
                if image.status in (Status.MATCHED, Status.UNBUILDABLE):
                    continue
                if re.search(patterns, image.name):
                    image.status = Status.MATCHED

                    ancestor_image = image
                    while (ancestor_image.parent is not None and
                           ancestor_image.parent.status != Status.MATCHED):
                        ancestor_image = ancestor_image.parent
                        # Parents of a buildable image must also be buildable.
                        ancestor_image.status = Status.MATCHED
                    LOG.debug('Image %s matched regex', image.name)
                else:
                    image.status = Status.UNMATCHED
        else:
            for image in self.images:
                if image.status != Status.UNBUILDABLE:
                    image.status = Status.MATCHED

        # Next, mark any skipped images.
        for image in self.images:
            if image.status != Status.MATCHED:
                continue
            # Skip image if --skip-existing was given and image exists.
            if (self.conf.skip_existing and image.in_engine_cache()):
                LOG.debug('Skipping existing image %s', image.name)
                image.status = Status.SKIPPED
            # Skip image if --skip-parents was given and image has children.
            elif self.conf.skip_parents and image.children:
                LOG.debug('Skipping parent image %s', image.name)
                image.status = Status.SKIPPED

    def summary(self):
        """Walk the dictionary of images statuses and print results."""
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
            'skipped': [],
            'unbuildable': [],
        }

        if self.image_statuses_good:
            LOG.info("=========================")
            LOG.info("Successfully built images")
            LOG.info("=========================")
            for name in sorted(self.image_statuses_good.keys()):
                LOG.info(name)
                results['built'].append({
                    'name': name,
                })

        if self.image_statuses_bad or self.image_statuses_allowed_to_fail:
            LOG.info("===========================")
            LOG.info("Images that failed to build")
            LOG.info("===========================")
            all_bad_statuses = self.image_statuses_bad.copy()
            all_bad_statuses.update(self.image_statuses_allowed_to_fail)
            for name, status in sorted(all_bad_statuses.items()):
                if name in self.image_statuses_allowed_to_fail:
                    LOG.error('%s Failed with status: %s (allowed to fail)',
                              name, status.value)
                else:
                    LOG.error('%s Failed with status: %s', name, status.value)

                results['failed'].append({
                    'name': name,
                    'status': status.value,
                })
                if self.conf.logs_dir and status == Status.ERROR:
                    linkname = os.path.join(self.conf.logs_dir,
                                            "000_FAILED_%s.log" % name)
                    try:
                        os.lstat(linkname)
                        os.remove(linkname)
                    except OSError:
                        pass

                    os.symlink("%s.log" % name, linkname)

        if self.image_statuses_unmatched:
            LOG.debug("=====================================")
            LOG.debug("Images not matched for build by regex")
            LOG.debug("=====================================")
            for name in sorted(self.image_statuses_unmatched.keys()):
                LOG.debug(name)
                results['not_matched'].append({
                    'name': name,
                })

        if self.image_statuses_skipped:
            LOG.info("===================================")
            LOG.info("Images skipped due to build options")
            LOG.info("===================================")
            for name in sorted(self.image_statuses_skipped.keys()):
                LOG.info(name)
                results['skipped'].append({
                    'name': name,
                })

        if self.image_statuses_unbuildable:
            LOG.info("=========================================")
            LOG.info("Images not buildable due to build options")
            LOG.info("=========================================")
            for name in sorted(self.image_statuses_unbuildable.keys()):
                LOG.info(name)
                results['unbuildable'].append({
                    'name': name,
                })

        if self.conf.format == 'json':

            def json_summary(f, **kwargs):
                json.dump(results, f, **kwargs)

            if self.conf.summary_json_file:
                try:
                    with open(self.conf.summary_json_file, "w") as f:
                        json_summary(f, indent=4)
                except OSError as e:
                    LOG.error(f'Failed to write JSON build summary to '
                              '{self.conf.summary_json_file}')
                    LOG.error(f'Exception caught: {e}')
                    sys.exit(1)

            else:
                # NOTE(mgoddard): Keep single line output for
                # backwards-compatibility.
                json_summary(sys.stdout)

        return results

    def get_image_statuses(self):
        if any([self.image_statuses_bad,
                self.image_statuses_good,
                self.image_statuses_unmatched,
                self.image_statuses_skipped,
                self.image_statuses_unbuildable,
                self.image_statuses_allowed_to_fail]):
            return (self.image_statuses_bad,
                    self.image_statuses_good,
                    self.image_statuses_unmatched,
                    self.image_statuses_skipped,
                    self.image_statuses_unbuildable,
                    self.image_statuses_allowed_to_fail)
        for image in self.images:
            if image.status == Status.BUILT:
                self.image_statuses_good[image.name] = image.status
            elif image.status == Status.UNMATCHED:
                self.image_statuses_unmatched[image.name] = image.status
            elif image.status == Status.SKIPPED:
                self.image_statuses_skipped[image.name] = image.status
            elif image.status == Status.UNBUILDABLE:
                self.image_statuses_unbuildable[image.name] = image.status
            else:
                if image.name in self.conf.allowed_to_fail:
                    self.image_statuses_allowed_to_fail[
                        image.name] = image.status
                else:
                    self.image_statuses_bad[image.name] = image.status
        return (self.image_statuses_bad,
                self.image_statuses_good,
                self.image_statuses_unmatched,
                self.image_statuses_skipped,
                self.image_statuses_unbuildable,
                self.image_statuses_allowed_to_fail)

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
                installation['enabled'] = self.conf[section]['enabled']
                installation['sha256'] = self.conf[section]['sha256']
            return installation

        all_sections = (set(self.conf._groups.keys()) |
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
                          logger=utils.make_a_logger(self.conf, image_name),
                          engine_client=self.engine_client)

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
            for addition in [
                match.group(0) for match in
                (re.search('^{}-additions-.+'.format(image.name),
                           section) for section in all_sections) if match]:
                try:
                    self.conf.register_opts(
                        common_config.get_source_opts(),
                        addition
                    )
                except cfg.DuplicateOptError:
                    LOG.debug('Addition %s already registered in config',
                              addition)
                image.additions.append(
                    process_source_installation(image, addition))

            self.images.append(image)

    def save_dependency(self, to_file):
        try:
            import graphviz
        except ImportError:
            LOG.error('"graphviz" is required for save dependency')
            raise
        dot = graphviz.Digraph(comment='Container Images Dependency')
        dot.body.extend(['rankdir=LR'])
        for image in self.images:
            if image.status not in [Status.MATCHED]:
                continue
            dot.node(image.name)
            if image.parent is not None:
                dot.edge(image.parent.name, image.name)

        with open(to_file, 'w') as f:
            f.write(dot.source)

    def list_images(self):
        for count, image in enumerate([
            image for image in self.images if image.status == Status.MATCHED
        ]):
            print(count + 1, ':', image.name)

    def list_dependencies(self):
        match = False
        for image in self.images:
            if image.status in [Status.MATCHED]:
                match = True
            if image.parent is None:
                base = image
        if not match:
            print('Nothing matched!')
            return

        def list_children(images, ancestry):
            children = next(iter(ancestry.values()))
            for image in images:
                if image.status not in [Status.MATCHED]:
                    continue
                if not image.children:
                    children.append(image.name)
                else:
                    newparent = {image.name: []}
                    children.append(newparent)
                    list_children(image.children, newparent)

        ancestry = {base.name: []}
        list_children(base.children, ancestry)
        json.dump(ancestry, sys.stdout, indent=2)

    def find_parents(self):
        """Associate all images with parents and children."""
        sort_images = dict()

        for image in self.images:
            sort_images[image.canonical_name] = image

        for parent_name, parent in sort_images.items():
            for image in sort_images.values():
                if (image.parent_name == parent_name):
                    parent.children.append(image)
                    image.parent = parent

    def build_queue(self, push_queue):
        """Organizes Queue list.

        Return a list of Queues that have been organized into a hierarchy
        based on dependencies
        """
        build_queue = queue.Queue()

        for image in self.images:
            if image.status in (Status.UNMATCHED, Status.SKIPPED,
                                Status.UNBUILDABLE):
                # Don't bother queuing up build tasks for things that
                # were not matched in the first place... (not worth the
                # effort to run them, if they won't be used anyway).
                continue
            # Build all root nodes, where a root is defined as having no parent
            # or having a parent that is explicitly being skipped.
            if image.parent is None or image.parent.status == Status.SKIPPED:
                build_queue.put(BuildTask(self.conf, image, push_queue))
                LOG.info('Added image %s to queue', image.name)

        return build_queue
