#!/usr/bin/python3

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
import collections
import glob
import os
import re
import sys

parser = argparse.ArgumentParser(
    description='Parse kolla build logs and extract useful information about '
                'the installed packages.')
parser.add_argument('-l', '--logdir',
                    help='Path to the build log files',
                    required=True)
parser.add_argument('-b', '--base',
                    help='The kolla base_distro',
                    required=True)
args = vars(parser.parse_args())

if args['base'] not in ['rocky', 'centos']:
    print("Non rpm-based distros are not yet supported.")
    sys.exit()

obsolete = {}
pkg_installs = collections.defaultdict(set)

for filename in glob.glob(os.path.join(args['logdir'], '*.log')):
    image = os.path.splitext(os.path.basename(filename))[0]
    with open(filename) as f:
        for line in f:
            m = re.search(r"Package (.+) is obsoleted by (.+),", line)
            if m:
                if not m.group(1) in obsolete:
                    obsolete[m.group(1)] = {'obsoleted_by': m.group(2),
                                            'images': [image]}
                else:
                    obsolete[m.group(1)]['images'].append(image)

            m = re.search(r"Package (.+)\..+ .+ will be installed", line)
            if m:
                pkg_installs[m.group(1)].add(image)

            m = re.search(r"Processing Dependency: (.+)\(", line)
            if m:
                pkg_installs[m.group(1)].add(image)

if obsolete:
    print("Found %s obsolete(s) package(s):" % len(obsolete))
    for pkg in obsolete:
        print("%s is obsoleted by %s (%s)" %
              (pkg,
               obsolete[pkg]['obsoleted_by'],
               ', '.join(obsolete[pkg]['images'])))
    print('')

move_to_base_candidates = [
    pkg for pkg in pkg_installs if len(pkg_installs[pkg]) > 10
    and not ('base' in pkg_installs[pkg]
             or 'openstack-base' in pkg_installs[pkg])
]

if move_to_base_candidates:
    print("Consider moving the following packages to a base image:")
    for pkg in move_to_base_candidates:
        print("%s (%s)" %
              (pkg,
               ', '.join(pkg_installs[pkg])))
