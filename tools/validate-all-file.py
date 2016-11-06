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
import fnmatch
import json
import logging
import os
import re
import sys

import jinja2


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

NEWLINE_EOF_INCLUDE_PATTERNS = ['*.j2', '*.yml', '*.py', '*.sh']
NEWLINE_EOF_EXCLUDE_PATTERNS = ['.tox', '.testrepository', '.git']

# Render json file by using jinja2 template is OK
JSON_J2_INCLUDE_PATTERNS = ['*.json.j2', '*.json']
JSON_J2_EXCLUDE_PATTERNS = ['.tox', '.testrepository', '.git']

logging.basicConfig()
LOG = logging.getLogger(__name__)


def check_newline_eof():
    includes = r'|'.join([fnmatch.translate(x)
                          for x in NEWLINE_EOF_INCLUDE_PATTERNS])
    excludes = r'|'.join([fnmatch.translate(x)
                          for x in NEWLINE_EOF_EXCLUDE_PATTERNS])
    return_code = 0

    def has_newline_eof(path):
        with open(path, 'r') as f:
            data = f.read()
            if data and data[-1] != '\n':
                LOG.error('%s file error: no newline at end of file', path)
                return False
        return True

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]
        for f in files:
            if not re.match(excludes, f) and re.match(includes, f):
                if not has_newline_eof(os.path.join(root, f)):
                    return_code = 1
    return return_code


def check_json_j2():
    includes = r'|'.join([fnmatch.translate(x)
                          for x in JSON_J2_INCLUDE_PATTERNS])
    excludes = r'|'.join([fnmatch.translate(x)
                          for x in JSON_J2_EXCLUDE_PATTERNS])
    return_code = 0

    def bool_filter(value):
        return True

    # Mock ansible hostvars variable, which is a nested dict
    def hostvars():
        return collections.defaultdict(hostvars)

    def validate_json_j2(root, filename):
        env = jinja2.Environment(  # nosec: not used to render HTML
            loader=jinja2.FileSystemLoader(root))
        env.filters['bool'] = bool_filter
        template = env.get_template(filename)
        # Mock ansible variables.
        context = {
            'hostvars': hostvars(),
            'cluster_interface': 'cluster_interface',
            'storage_interface': 'storage_interface',
            'inventory_hostname': 'hostname'
        }
        data = template.render(**context)
        json.loads(data)
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]
        for filename in files:
            if not re.match(excludes, filename) and \
                    re.match(includes, filename):
                fullpath = os.path.join(root, filename)
                try:
                    validate_json_j2(root, filename)
                except (ValueError, jinja2.exceptions.TemplateError):
                    return_code = 1
                    LOG.exception('%s file error', fullpath)
    return return_code


def main():
    checks = (
        check_newline_eof,
        check_json_j2
    )
    return sum([check() for check in checks])

if __name__ == "__main__":
    sys.exit(main())
