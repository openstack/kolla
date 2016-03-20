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
import os
import re
import sys

from bs4 import BeautifulSoup as bs
from oslo_config import cfg
import pkg_resources
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..'))

# NOTE(SamYaple): Update the search patch to prefer PROJECT_ROOT as the source
#                 of packages to import if we are using local tools/build.py
#                 instead of pip installed kolla-build tool
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kolla.common import config as common_config


# Use an OrderedDict to ensure the results are displayed alphabetically
MAJOR_VERSIONS_MAP = collections.OrderedDict([
    ('ceilometer', 5),
    ('cinder', 7),
    ('designate', 1),
    ('glance', 11),
    ('gnocchi', 1),
    ('heat', 5),
    ('horizon', 8),
    ('ironic', 4),
    ('keystone', 8),
    ('magnum', 1),
    ('murano', 1),
    ('neutron', 7),
    ('nova', 12),
    ('swift', 2),
    ('zaqar', 1)
])

TARBALLS_BASE_URL = 'http://tarballs.openstack.org'
VERSIONS = dict()


def retrieve_upstream_versions():
    upstream_versions = dict()
    for project in MAJOR_VERSIONS_MAP:
        winner = None
        series = MAJOR_VERSIONS_MAP[project]
        base = '{}/{}'.format(TARBALLS_BASE_URL, project)
        r = requests.get(base)
        s = bs(r.text, 'html.parser')

        for link in s.find_all('a'):
            version = link.get('href')
            if (version.endswith('.tar.gz') and
                    version.startswith('{}-{}'.format(project, series))):
                split = '{}-|.tar.gz'.format(project)
                candidate = re.split(split, version)[1]
                if not winner or more_recent(candidate, winner):
                    winner = candidate

        if not winner:
            print('Could not find version for {}'.format(project))
            continue

        upstream_versions[project] = winner

    VERSIONS['upstream'] = upstream_versions


def retrieve_local_versions(conf):
    local_versions = dict()
    for project in MAJOR_VERSIONS_MAP:
        series = MAJOR_VERSIONS_MAP[project]
        for project_section in [match.group(0) for match in
                                (re.search('^{}(?:-base)?$'.format(project),
                                           section) for section in
                                 conf._groups) if match]:
            archive = conf[project_section]['location'].split('/')[-1]
            if (archive.endswith('.tar.gz') and
                    archive.startswith('{}-{}'.format(project, series))):
                split = '{}-|.tar.gz'.format(project)
                local_versions[project] = re.split(split, archive)[1]

    VERSIONS['local'] = local_versions


def more_recent(candidate, reference):
    return pkg_resources.parse_version(candidate) > \
        pkg_resources.parse_version(reference)


def diff_link(project, old_ref, new_ref):
    return "https://github.com/openstack/{}/compare/{}...{}".format(
        project, old_ref, new_ref)


def compare_versions():
    up_to_date = True
    for project in VERSIONS['upstream']:
        if project in VERSIONS['local']:
            upstream_version = VERSIONS['upstream'][project]
            local_version = VERSIONS['local'][project]
            if more_recent(upstream_version, local_version):
                print("{} has newer version {} > {}, see diff at {}".format(
                    project, upstream_version, local_version,
                    diff_link(project, local_version, upstream_version)))
                up_to_date = False
    if up_to_date:
        print("Everything is up to date")


def main():
    conf = cfg.ConfigOpts()
    common_config.parse(conf, sys.argv[1:], prog='kolla-build')

    retrieve_upstream_versions()
    retrieve_local_versions(conf)

    compare_versions()

if __name__ == '__main__':
    main()
