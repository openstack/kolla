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

import argparse
import logging
import os
import re
import subprocess  # nosec
import sys

import yaml


# NOTE(SamYaple): Update the search path to prefer PROJECT_ROOT as the source
#                 of packages to import if we are using local tools instead of
#                 pip installed kolla tools
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from kolla.common import config


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

RELEASE_REPO = 'https://github.com/openstack/releases'
TARGET = '.releases'

SKIP_PROJECTS = {
    'gnocchi-base': 'Gnocchi is not managed by openstack/releases project',
    'rally': 'Rally is not managed by openstack/releases project',
    'nova-novncproxy': ('nova-novncproxy is not managed by'
                        ' openstack/releases project'),
    'nova-spicehtml5proxy': ('nova-spicehtml5proxy is not managed'
                             ' by openstack/releases project'),
    'openstack-base': 'There is no tag for requirements project'
}

RE_DEFAULT_BRANCH = re.compile('^defaultbranch=stable/(.*)')
RE_FILENAME = re.compile('(?P<project_name>.*)-(?P<tag>[^-]*).tar.gz')


def update_releases_repo():
    if not os.path.exists(TARGET):
        cmd = ['git', 'clone', RELEASE_REPO, TARGET]
    else:
        cmd = ['git', '--git-dir', os.path.join(TARGET, '.git'), '--work-tree',
               TARGET, 'pull']
    subprocess.call(cmd)  # nosec


def get_default_branch():
    gitreview_file = os.path.join(PROJECT_ROOT, '.gitreview')
    if not os.path.exists(gitreview_file):
        return

    with open(gitreview_file, 'r') as gitreview:
        for line in gitreview:
            branches = RE_DEFAULT_BRANCH.findall(line)
            if branches:
                return branches[0]


def load_all_info(openstack_release):
    projects = {}
    release_path = os.path.join(TARGET, 'deliverables', openstack_release)

    if not os.path.exists(release_path):
        raise ValueError(
            'Can not find openstack release: "%s"' % openstack_release)

    for deliverable in os.listdir(release_path):
        if not deliverable.endswith('.yaml'):
            continue
        with open(os.path.join(release_path, deliverable)) as f:
            info = yaml.safe_load(f)
        if 'releases' in info and len(info['releases']) > 0:
            latest_release = info['releases'][-1]
            latest_version = latest_release['version']
            for project in latest_release['projects']:
                project_name = project['repo'].split('/')[-1]
                projects[project_name] = latest_version
                if 'tarball-base' in project:
                    projects[project['tarball-base']] = latest_version
    return projects


def main():
    parser = argparse.ArgumentParser(
        description='Check and update OpenStack service version.')
    parser.add_argument('--openstack-release', '-r',
                        default=get_default_branch(),
                        help='OpenStack release name')
    parser.add_argument('--include-independent', '-i',
                        default=False, action='store_true',
                        help='Whether update independent projects')
    parser.add_argument('--check', '-c',
                        default=False, action='store_true',
                        help='Run without update config.py file')
    conf = parser.parse_args(sys.argv[1:])

    if not conf.openstack_release:
        raise ValueError('Can not detect openstack release. Please assign'
                         ' it through "--openstack-release" parameter')

    LOG.info('Update using openstack release: "%s"', conf.openstack_release)

    if conf.check:
        LOG.info('Run in check only mode')

    update_releases_repo()

    projects = load_all_info(openstack_release=conf.openstack_release)
    independents_projects = load_all_info(openstack_release='_independent')

    with open(os.path.join(PROJECT_ROOT, 'kolla/common/config.py')) as f:
        config_py = f.read()

    for key in sorted(config.SOURCES):
        independent_project = False
        value = config.SOURCES[key]
        if key in SKIP_PROJECTS:
            LOG.info('%s is skiped: %s', key, SKIP_PROJECTS[key])
            continue
        # get project name from location
        location = value['location']
        filename = os.path.basename(location)
        match = RE_FILENAME.match(filename)
        if match:
            project_name, old_tag = match.groups()
        else:
            raise ValueError('Can not parse "%s"' % filename)

        latest_tag = projects.get(project_name, None)
        if not latest_tag:
            latest_tag = independents_projects.get(project_name, None)
            if latest_tag:
                independent_project = True
            else:
                LOG.warning('Can not find %s project release', project_name)
                continue
        if latest_tag and old_tag != latest_tag:
            if independent_project and not conf.include_independent:
                LOG.warning('%s is an independent project, please update it'
                            ' manually. Possible need upgrade from %s to %s',
                            project_name, old_tag, latest_tag)
                continue
            LOG.info('Update %s from %s to %s', project_name, old_tag,
                     latest_tag)
            old_str = '{}-{}'.format(project_name, old_tag)
            new_str = '{}-{}'.format(project_name, latest_tag)
            config_py = config_py.replace(old_str, new_str)

    if not conf.check:
        with open(os.path.join(PROJECT_ROOT, 'kolla/common/config.py'),
                  'w') as f:
            f.write(config_py)


if __name__ == '__main__':
    main()
