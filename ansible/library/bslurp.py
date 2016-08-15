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

# This module has been relicensed from the source below:
# https://github.com/SamYaple/yaodu/blob/master/ansible/library/bslurp

DOCUMENTATION = '''
---
module: bslurp
short_description: Slurps a file from a remote node
description:
     - Used for fetching a binary blob containing the file, then push that file
       to other hosts.
options:
  src:
    description:
      - File to fetch. When dest is used, src is expected to be a str with data
    required: True
    type: str
  compress:
    description:
      - Compress file with zlib
    default: True
    type: bool
  dest:
    description:
      - Where to write out binary blob
    required: False
    type: str
  mode:
    description:
      - Destination file permissions
    default: '0644'
    type: str
  sha1:
    description:
      - sha1 hash of the underlying data
    default: None
    type: bool
author: Sam Yaple
'''

EXAMPLES = '''
Distribute a file from single to many hosts:

- hosts: web_servers
  tasks:
    - name: Pull in web config
      bslurp: src="/path/to/file"
      register: file_data
      run_once: True
    - name: Push if changed
      bslurp:
        src: "{{ file_data.content }}"
        dest: "{{ file_data.source }}"
        mode: "{{ file_data.mode }}"
        sha1: "{{ file_data.sha1 }}"

Distribute multiple files from single to many hosts:

- hosts: web_servers
  tasks:
    - name: Pull in web config
      bslurp: src="{{ item }}"
      with_items:
        - "/path/to/file1"
        - "/path/to/file2"
        - "/path/to/file3"
      register: file_data
      run_once: True
    - name: Push if changed
      bslurp:
        src: "{{ item.content }}"
        dest: "{{ item.source }}"
        mode: "{{ item.mode }}"
        sha1: "{{ item.sha1 }}"
      with_items: file_data.results

Distribute a file to many hosts without compression; Change
permissions on dest:

- hosts: web_servers
  tasks:
    - name: Pull in web config
      bslurp: src="/path/to/file"
      register: file_data
      run_once: True
    - name: Push if changed
      bslurp:
        src: "{{ file_data.content }}"
        dest: "/new/path/to/file"
        mode: "0777"
        compress: False
        sha1: "{{ file_data.sha1 }}"
'''

import base64
import hashlib
import os
import traceback
import zlib


def copy_from_host(module):
    compress = module.params.get('compress')
    src = module.params.get('src')

    if not os.path.exists(src):
        module.fail_json(msg="file not found: {}".format(src))
    if not os.access(src, os.R_OK):
        module.fail_json(msg="file is not readable: {}".format(src))

    mode = oct(os.stat(src).st_mode & 0o777)

    with open(src, 'rb') as f:
        raw_data = f.read()

    sha1 = hashlib.sha1(raw_data).hexdigest()
    data = zlib.compress(raw_data) if compress else raw_data

    module.exit_json(content=base64.b64encode(data), sha1=sha1, mode=mode,
                     source=src)


def copy_to_host(module):
    compress = module.params.get('compress')
    dest = module.params.get('dest')
    mode = int(module.params.get('mode'), 0)
    sha1 = module.params.get('sha1')
    src = module.params.get('src')

    data = base64.b64decode(src)
    raw_data = zlib.decompress(data) if compress else data

    if sha1:
        if os.path.exists(dest):
            if os.access(dest, os.R_OK):
                with open(dest, 'rb') as f:
                    if hashlib.sha1(f.read()).hexdigest() == sha1:
                        module.exit_json(changed=False)
            else:
                module.exit_json(failed=True, changed=False,
                                 msg='file is not accessible: {}'.format(dest))

        if sha1 != hashlib.sha1(raw_data).hexdigest():
            module.exit_json(failed=True, changed=False,
                             msg='sha1 sum does not match data')

    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT, mode), 'wb') as f:
        f.write(raw_data)

    module.exit_json(changed=True)


def main():
    argument_spec = dict(
        compress=dict(default=True, type='bool'),
        dest=dict(type='str'),
        mode=dict(default='0644', type='str'),
        sha1=dict(default=None, type='str'),
        src=dict(required=True, type='str')
    )
    module = AnsibleModule(argument_spec)

    dest = module.params.get('dest')

    try:
        if dest:
            copy_to_host(module)
        else:
            copy_from_host(module)
    except Exception:
        module.exit_json(failed=True, changed=True,
                         msg=repr(traceback.format_exc()))


# import module snippets
from ansible.module_utils.basic import *  # noqa
if __name__ == '__main__':
    main()
