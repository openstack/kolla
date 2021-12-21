#!/usr/bin/env python3

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

from kolla.common import config  # noqa


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

RELEASE_REPO = 'https://github.com/openstack/releases'
TARGET = '.releases'

SKIP_PROJECTS = {
    'gnocchi-base': 'Gnocchi is not managed by openstack/releases project',
    'monasca-thresh': 'Package not published in tarballs.openstack.org',
}

# NOTE(hrw): those projects we take as they are they may have just one old
# release or no stable branch tarballs
ALWAYS_USE_VERSION_PROJECTS = {
}

# NOTE(hrw): those projects have different names for release tarballs (first
# column) and other for branch tarballs
RENAME_PROJECTS = {
    'kuryr-lib': 'kuryr',
    'openstack-cyborg': 'cyborg',
    'openstack-heat': 'heat',
    'openstack-placement': 'placement',
    'python-watcher': 'watcher',
    'requirements-stable': 'requirements',
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
            if latest_version.endswith('-em') and len(info['releases']) > 1:
                # Ignore Extended Maintenance (EM) releases, e.g. pike-em.
                latest_release = info['releases'][-2]
                latest_version = latest_release['version']
            for project in latest_release['projects']:
                project_name = project['repo'].split('/')[-1]

                if 'tarball-base' in project:
                    tarball_base = project['tarball-base']
                elif 'repository-settings' in info:
                    try:
                        repo = project['repo']
                        repository_settings = info['repository-settings'][repo]
                        tarball_base = repository_settings['tarball-base']
                    except KeyError:
                        tarball_base = project_name

                projects[project_name] = {'latest_version': latest_version,
                                          'tarball_base': tarball_base}
                projects[tarball_base] = {'latest_version': latest_version,
                                          'tarball_base': tarball_base}

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
    parser.add_argument('--versioned-releases', '-v',
                        default=False, action='store_true',
                        help='Use versioned releases tarballs')
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
            LOG.info('%s is skipped: %s', key, SKIP_PROJECTS[key])
            continue
        # get project name from location
        location = value['location']
        filename = os.path.basename(location)
        match = RE_FILENAME.match(filename)
        if match:
            project_name, old_tag = match.groups()
        else:
            raise ValueError('Can not parse "%s"' % filename)

        if (project_name == "requirements" or
                (not conf.versioned_releases and
                 project_name not in ALWAYS_USE_VERSION_PROJECTS)):
            # Use the stable branch for requirements.
            latest_tag = "stable-{}".format(conf.openstack_release)
            tarball_base = project_name
            if project_name in RENAME_PROJECTS:
                tarball_base = RENAME_PROJECTS[project_name]
        elif project_name in projects:
            latest_tag = projects[project_name]['latest_version']
            tarball_base = projects[project_name]['tarball_base']
        elif project_name in independents_projects:
            latest_tag = independents_projects[project_name]['latest_version']
            tarball_base = independents_projects[project_name]['tarball_base']
            independent_project = True
        else:
            LOG.warning('Can not find %s project release',
                        project_name)
            continue

        if latest_tag and old_tag != latest_tag:
            if independent_project and not conf.include_independent:
                LOG.warning('%s is an independent project, please update it'
                            ' manually. Possible need upgrade from %s to %s',
                            project_name, old_tag, latest_tag)
                continue
            LOG.info('Update %s from %s to %s %s', project_name, old_tag,
                     tarball_base, latest_tag)
            # starting "'" to replace whole filenames not partial ones
            # so nova does not change blazar-nova
            old_str = "'{}-{}".format(project_name, old_tag)
            new_str = "'{}-{}".format(tarball_base, latest_tag)
            config_py = config_py.replace(old_str, new_str)

    if not conf.check:
        with open(os.path.join(PROJECT_ROOT, 'kolla/common/config.py'),
                  'w') as f:
            f.write(config_py)


if __name__ == '__main__':
    main()
