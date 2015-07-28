#!/usr/bin/python

# Copyright 2015 Sam Yaple
#
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

DOCUMENTATION = '''
---
module: merge_configs
short_description: Merge ini-style configs
description:
     - ConfigParser is used to merge several ini-style configs into one
options:
  dest:
    description:
      - The destination file name
    required: True
    type: str
  sources:
    description:
      - A list of files on the destination node to merge together
    default: None
    required: True
    type: str
author: Sam Yaple
'''

EXAMPLES = '''
Merge multiple configs:

- hosts: database
  tasks:
    - name: Merge configs
      merge_configs:
        sources:
          - "/tmp/config_1.cnf"
          - "/tmp/config_2.cnf"
          - "/tmp/config_3.cnf"
        dest:
          - "/etc/mysql/my.cnf"
'''

from ConfigParser import ConfigParser
from cStringIO import StringIO

def main():
    module = AnsibleModule(
        argument_spec = dict(
            sources = dict(required=True, type='list'),
            dest = dict(required=True, type='str'),
        )
    )

    try:
        sources = module.params.pop('sources')
        dest = module.params.pop('dest')

        changed = False

        config = ConfigParser()

        for source_file in sources:
            config.read(source_file)

        if os.path.exists(dest) and os.access(dest, os.R_OK):
            fakedest = StringIO()
            config.write(fakedest)
            with open(dest, 'rb') as f:
                files_match = f.read() == fakedest.getvalue()

        else:
            files_match = False

        if not files_match:
            changed = True
            with open(dest, 'wb') as f:
                config.write(f)

        module.exit_json(changed=changed)
    except Exception, e:
        module.exit_json(failed=True, changed=changed, msg=repr(e))


# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
