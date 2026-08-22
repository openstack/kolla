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

"""Check that every buildable-from-source entry in kolla/common/sources.yaml
has a matching CI override in
roles/kolla-build-config/defaults/main.yml (kolla_build_sources), that
each such project is declared in the kolla-base job's required-projects
in zuul.d/base.yaml, and that any pinned git reference in sources.yaml
matches the override-checkout used to fetch it in CI. This ensures CI
builds every source from a Zuul-cached git checkout instead of
downloading a tarball from tarballs.opendev.org.
"""

import os
import sys

import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from kolla.common.sources import SOURCES  # noqa: E402

BUILD_SOURCES_PATH = os.path.join(
    PROJECT_ROOT, 'roles', 'kolla-build-config', 'defaults', 'main.yml')
ZUUL_BASE_PATH = os.path.join(PROJECT_ROOT, 'zuul.d', 'base.yaml')

# Sources deliberately not covered by kolla_build_sources, with the
# reason a git-checkout override doesn't apply to them.
EXCLUDED_SOURCES = {
    # Binary releases downloaded from GitHub, not built from a source
    # checkout.
    'etcd',
    'letsencrypt-lego',
    'magnum-conductor-plugin-helm',
    # GitHub projects that are not registered with the OpenStack Zuul
    # tenant (unlike gnocchixyz/gnocchi), so they can't be required-projects.
    'kerbside-base',
    'mariadb-server-plugin-mariadb-docker',
}


def is_excluded(name):
    return name in EXCLUDED_SOURCES or name.startswith('prometheus-')


def as_list(section_names):
    if isinstance(section_names, str):
        return [section_names]
    return list(section_names)


def load_kolla_build_sources():
    with open(BUILD_SOURCES_PATH) as f:
        return yaml.safe_load(f)['kolla_build_sources']


def load_required_projects():
    """Parse the kolla-base job's required-projects in zuul.d/base.yaml.

    Returns (all project names, {project: override-checkout}).
    """
    with open(ZUUL_BASE_PATH) as f:
        docs = yaml.safe_load(f)

    job = next(doc['job'] for doc in docs
               if 'job' in doc and doc['job']['name'] == 'kolla-base')

    all_projects = set()
    checkouts = {}
    for entry in job.get('required-projects', []):
        if isinstance(entry, str):
            all_projects.add(entry)
        else:
            all_projects.add(entry['name'])
            if 'override-checkout' in entry:
                checkouts[entry['name']] = entry['override-checkout']
    return all_projects, checkouts


def main():
    kolla_build_sources = load_kolla_build_sources()
    required_projects, override_checkouts = load_required_projects()

    covered = set()
    for section_names in kolla_build_sources.values():
        covered.update(as_list(section_names))

    buildable = {name for name in SOURCES if not is_excluded(name)}

    missing = sorted(buildable - covered)
    stale = sorted(covered - set(SOURCES))
    redundant_exclusions = sorted(
        name for name in EXCLUDED_SOURCES if name not in SOURCES)
    not_required = sorted(set(kolla_build_sources) - required_projects)

    ref_errors = []
    for project, section_names in sorted(kolla_build_sources.items()):
        for section in as_list(section_names):
            info = SOURCES.get(section)
            if not info or info.get('type') != 'git':
                continue
            expected_ref = info.get('reference')
            actual = override_checkouts.get(project)
            if actual is None:
                ref_errors.append(
                    f"{project} ({section}) is pinned to reference "
                    f"'{expected_ref}' in sources.yaml but has no "
                    "override-checkout in zuul.d/base.yaml "
                    "required-projects")
            elif actual != expected_ref:
                ref_errors.append(
                    f"{project} ({section}): sources.yaml reference "
                    f"'{expected_ref}' != required-projects "
                    f"override-checkout '{actual}'")

    for project, checkout in sorted(override_checkouts.items()):
        section_names = kolla_build_sources.get(project)
        if section_names is None:
            continue
        git_sections = [s for s in as_list(section_names)
                        if SOURCES.get(s, {}).get('type') == 'git']
        if not git_sections:
            ref_errors.append(
                f"{project} has override-checkout '{checkout}' in "
                "required-projects but none of its kolla_build_sources "
                "sections are type 'git' in sources.yaml")

    if missing:
        print("ERROR: sources.yaml entries missing a kolla_build_sources "
              "override in roles/kolla-build-config/defaults/main.yml:")
        for name in missing:
            print(f"  {name}")

    if stale:
        print("ERROR: kolla_build_sources overrides referencing sections "
              "that no longer exist in kolla/common/sources.yaml:")
        for name in stale:
            print(f"  {name}")

    if redundant_exclusions:
        print("ERROR: EXCLUDED_SOURCES entries referencing sections that "
              "no longer exist in kolla/common/sources.yaml, remove them:")
        for name in redundant_exclusions:
            print(f"  {name}")

    if not_required:
        print("ERROR: kolla_build_sources projects missing from the "
              "kolla-base job's required-projects in zuul.d/base.yaml:")
        for name in not_required:
            print(f"  {name}")

    if ref_errors:
        print("ERROR: git reference mismatches between sources.yaml and "
              "zuul.d/base.yaml required-projects:")
        for msg in ref_errors:
            print(f"  {msg}")

    return 1 if (missing or stale or redundant_exclusions or not_required
                 or ref_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
