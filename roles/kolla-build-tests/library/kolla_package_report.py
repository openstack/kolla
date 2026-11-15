#!/usr/bin/python

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
import glob
import os
import re

DOCUMENTATION = '''
---
module: kolla_package_report
short_description: Report packages installed separately in many kolla images
description:
  - Compares the packages installed in each kolla image with its parent
    image, using one file per image listing installed package names.
  - Reports packages installed separately in more than I(threshold) images,
    with the closest common parent image they could be moved to, and
    packages an image removes compared with its parent.
options:
  logdir:
    description: Path to the kolla-build log files, used to find each
      image's parent.
    required: true
    type: path
  pkgdir:
    description: Path to the package lists, one C(<image>.txt) per image
      with one package name per line.
    required: true
    type: path
  threshold:
    description: Report packages installed separately in more than this many
      images.
    type: int
    default: 10
'''

EXAMPLES = '''
- name: Report packages installed in kolla images
  kolla_package_report:
    logdir: /home/zuul/zuul-output/logs/kolla/build
    pkgdir: /home/zuul/zuul-output/logs/kolla/packages
  register: result
'''

RETURN = '''
candidates:
  description: Packages to consider moving to a parent image.
  returned: always
  type: list
removals:
  description: Packages each image removes compared with its parent.
  returned: always
  type: list
skipped:
  description: Images skipped because their parent has no package list.
  returned: always
  type: list
package_warnings:
  description: One line per candidate and per image removing packages.
  returned: always
  type: list
report:
  description: Human readable report.
  returned: always
  type: str
'''

# Lines longer than this are JSON-escaped output (e.g. bifrost's ansible
# run) and are expensive to match.
MAX_LINE = 8192

# docker (BuildKit): INFO:kolla.common.utils.<image>:#<step> [<secs>] <payload>
# podman:            INFO:kolla.common.utils.<image>:<payload>
PREFIX = re.compile(
    r'^[A-Z]+:kolla\.common\.utils\.[^:]+:'
    r'(?:#(\d+) (?:\d+(?:\.\d+)? ?)?)?(.*)$')
FROM = re.compile(r'^(?:\[\s*1/\d+\]|STEP 1/\d+:) FROM \S*?/([^/:\s]+):')

# rpm's pseudo-package for imported GPG keys, not an installed package.
IGNORED_PACKAGES = {'gpg-pubkey'}


def payloads(lines):
    for line in lines:
        if len(line) > MAX_LINE:
            continue
        m = PREFIX.match(line.rstrip('\n'))
        if m:
            yield m.group(1), m.group(2)


def parse_parent(lines):
    """Return the image named in the first FROM line of a build log."""
    for _, p in payloads(lines):
        m = FROM.match(p)
        if m:
            return m.group(1)
    return None


def read_packages(path):
    with open(path) as f:
        return {line.strip() for line in f
                if line.strip() and line.strip() not in IGNORED_PACKAGES}


def ancestors(image, parents):
    """Return the parent chain of an image, root first."""
    chain, seen = [], {image}
    cur = parents.get(image)
    while cur and cur not in seen:
        chain.append(cur)
        seen.add(cur)
        cur = parents.get(cur)
    return chain[::-1]


def common_parent(images, parents):
    common = None
    for level in zip(*[ancestors(i, parents) for i in images]):
        if len(set(level)) != 1:
            break
        common = level[0]
    return common


def analyse(logdir, pkgdir, threshold):
    parents = {}
    for filename in sorted(glob.glob(os.path.join(logdir, '*.log'))):
        image = os.path.splitext(os.path.basename(filename))[0]
        with open(filename, errors='replace') as f:
            parents[image] = parse_parent(f)
    # Only images built in this run count as parents.
    parents = {i: p if p in parents else None for i, p in parents.items()}

    pkgs = {}
    for filename in sorted(glob.glob(os.path.join(pkgdir, '*.txt'))):
        image = os.path.splitext(os.path.basename(filename))[0]
        pkgs[image] = read_packages(filename)

    added, removals, skipped = {}, [], []
    for image in sorted(pkgs):
        parent = parents.get(image)
        if parent is None:
            added[image] = pkgs[image]
        elif parent in pkgs:
            added[image] = pkgs[image] - pkgs[parent]
            removed = pkgs[parent] - pkgs[image]
            if removed:
                removals.append({'image': image,
                                 'parent': parent,
                                 'packages': sorted(removed)})
        else:
            skipped.append(image)

    where = collections.defaultdict(set)
    for image, image_pkgs in added.items():
        for pkg in image_pkgs:
            where[pkg].add(image)

    candidates = [{'package': pkg,
                   'images': sorted(images),
                   'suggested_parent': common_parent(images, parents)}
                  for pkg, images in where.items() if len(images) > threshold]
    candidates.sort(key=lambda c: (-len(c['images']), c['package']))

    warnings = []
    for c in candidates:
        if c['suggested_parent']:
            warnings.append(
                '%s is installed by %d images separately; consider '
                'installing it once in %s instead' %
                (c['package'], len(c['images']), c['suggested_parent']))
        else:
            warnings.append(
                '%s is installed by %d images separately, but they have no '
                'common parent image' % (c['package'], len(c['images'])))
    for r in removals:
        warnings.append('%s removes %s, which its parent %s has installed' %
                        (r['image'], ', '.join(r['packages']), r['parent']))
    return {'candidates': candidates,
            'removals': removals,
            'skipped': skipped,
            'warnings': warnings}


def format_report(report):
    lines = []
    if report['candidates']:
        lines.append(
            "Consider moving the following packages to a parent image:")
        for c in report['candidates']:
            lines.append("%s -> %s (%s)" %
                         (c['package'],
                          c['suggested_parent'] or '(no common parent)',
                          ', '.join(c['images'])))
        lines.append('')

    if report['removals']:
        lines.append("Packages removed compared with the parent image:")
        for r in report['removals']:
            lines.append("%s (parent %s): %s" %
                         (r['image'], r['parent'], ', '.join(r['packages'])))
        lines.append('')

    if report['skipped']:
        lines.append("Skipped (parent has no package list): %s" %
                     ', '.join(report['skipped']))
        lines.append('')
    return '\n'.join(lines)


def main():
    # Imported here so the parsing functions can be unit tested on Python
    # versions without ansible-core (see test-requirements.txt).
    from ansible.module_utils.basic import AnsibleModule

    module = AnsibleModule(
        argument_spec=dict(
            logdir=dict(type='path', required=True),
            pkgdir=dict(type='path', required=True),
            threshold=dict(type='int', default=10),
        ),
        supports_check_mode=True,
    )
    p = module.params
    for opt in ('logdir', 'pkgdir'):
        if not os.path.isdir(p[opt]):
            module.fail_json(msg='%s is not a directory' % p[opt])

    report = analyse(p['logdir'], p['pkgdir'], p['threshold'])
    # 'warnings' is reserved for Ansible's own warnings.
    module.exit_json(changed=False,
                     candidates=report['candidates'],
                     removals=report['removals'],
                     skipped=report['skipped'],
                     package_warnings=report['warnings'],
                     report=format_report(report))


if __name__ == '__main__':
    main()
