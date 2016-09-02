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

import collections
import logging
import os
import re
import sys

import bs4
from oslo_config import cfg
import pkg_resources
import prettytable
import requests

# NOTE(SamYaple): Update the search path to prefer PROJECT_ROOT as the source
#                 of packages to import if we are using local tools instead of
#                 pip installed kolla tools
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kolla.common import config as common_config

logging.basicConfig(format="%(message)s")
LOG = logging.getLogger('version-check')

# Filter list for non-projects
NOT_PROJECTS = [
    'nova-novncproxy',
    'nova-spicehtml5proxy',
    'openstack-base',
    'profiles'
]
TARBALLS_BASE_URL = 'http://tarballs.openstack.org'
VERSIONS = {'local': dict()}


def retrieve_upstream_versions():
    upstream_versions = dict()
    for project in VERSIONS['local']:
        winner = None
        series = VERSIONS['local'][project].split('.')[0]
        base = '{}/{}'.format(TARBALLS_BASE_URL, project)
        LOG.debug("Getting latest version for project %s from %s",
                  project, base)
        r = requests.get(base)
        s = bs4.BeautifulSoup(r.text, 'html.parser')

        for link in s.find_all('a'):
            version = link.get('href')
            if (version.endswith('.tar.gz') and
                    version.startswith('{}-{}'.format(project, series))):
                split = '{}-|.tar.gz'.format(project)
                candidate = re.split(split, version)[1]
                # Ignore 2014, 2015 versions as they are older
                if candidate.startswith('201'):
                    continue
                if not winner or more_recent(candidate, winner):
                    winner = candidate

        if not winner:
            LOG.warning("Could not find a version for %s", project)
            continue

        if '-' in winner:
            winner = winner.split('-')[1]
        upstream_versions[project] = winner
        LOG.debug("Found latest version %s for project %s", winner, project)

    VERSIONS['upstream'] = collections.OrderedDict(
        sorted(upstream_versions.items()))


def retrieve_local_versions(conf):
    for section in common_config.SOURCES:
        if section in NOT_PROJECTS:
            continue

        project = section.split('-')[0]

        if section not in conf.list_all_sections():
            LOG.debug("Project %s not found in configuration file, using "
                      "default from kolla.common.config", project)
            raw_version = common_config.SOURCES[section]['location']
        else:
            raw_version = getattr(conf, section).location

        version = raw_version.split('/')[-1].split('.tar.gz')[0]
        if '-' in version:
            version = version.split('-')[1]

        LOG.debug("Use local version %s for project %s", version, project)
        VERSIONS['local'][project] = version


def more_recent(candidate, reference):
    return pkg_resources.parse_version(candidate) > \
        pkg_resources.parse_version(reference)


def diff_link(project, old_ref, new_ref):
    return "https://github.com/openstack/{}/compare/{}...{}".format(
        project, old_ref, new_ref)


def compare_versions():
    up_to_date = True
    result = prettytable.PrettyTable(["Project", "Current version",
                                      "Latest version", "Comparing changes"])
    result.align = "l"

    for project in VERSIONS['upstream']:
        if project not in VERSIONS['local']:
            continue

        upstream_version = VERSIONS['upstream'][project]
        local_version = VERSIONS['local'][project]

        if more_recent(upstream_version, local_version):
            result.add_row([
                project,
                VERSIONS['local'][project],
                VERSIONS['upstream'][project],
                diff_link(project, local_version, upstream_version)
            ])
            up_to_date = False

    if up_to_date:
        result = "Everything is up to date"

    print(result)


def main():
    conf = cfg.ConfigOpts()
    common_config.parse(conf, sys.argv[1:], prog='version-check')

    if conf.debug:
        LOG.setLevel(logging.DEBUG)

    retrieve_local_versions(conf)
    retrieve_upstream_versions()

    compare_versions()

if __name__ == '__main__':
    main()
