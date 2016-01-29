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
# https://github.com/SamYaple/yaodu/blob/master/ansible/library/ceph_osd_list

DOCUMENTATION = '''
---
module: find_disks
short_description: Return list of devices containing a specfied name or label
description:
     - This will return a list of all devices with either GPT partition name
       or filesystem label of the name specified.
options:
  match_mode:
    description:
      - Label match mode, either strict or prefix
    default: 'strict'
    required: False
    choices: [ "strict", "prefix" ]
    type: str
  name:
    description:
      - Partition name or filesystem label
    required: True
    type: str
    aliases: [ 'partition_name' ]
author: Sam Yaple
'''

EXAMPLES = '''
- hosts: ceph-osd
  tasks:
    - name: Return all valid formated devices with the name KOLLA_CEPH_OSD
      find_disks:
          name: 'KOLLA_CEPH_OSD'
      register: osds

- hosts: swift-object-server
  tasks:
    - name: Return all valid devices with the name KOLLA_SWIFT
      find_disks:
          name: 'KOLLA_SWIFT'
      register: swift_disks

- hosts: swift-object-server
  tasks:
    - name: Return all valid devices with wildcard name 'swift_d*'
      find_disks:
          name: 'swift_d' match_mode: 'prefix'
      register: swift_disks
'''

import json
import pyudev


def main():
    argument_spec = dict(
        match_mode=dict(required=False, choices=['strict', 'prefix'],
                        default='strict'),
        name=dict(aliases=['partition_name'], required=True, type='str')
    )
    module = AnsibleModule(argument_spec)
    match_mode = module.params.get('match_mode')
    name = module.params.get('name')

    def is_dev_matched_by_name(dev, name):
        if dev.get('DEVTYPE', '') == 'partition':
            dev_name = dev.get('ID_PART_ENTRY_NAME', '')
        else:
            dev_name = dev.get('ID_FS_LABEL', '')

        if match_mode == 'strict':
            return dev_name == name
        elif match_mode == 'prefix':
            return dev_name.startswith(name)
        else:
            return False

    try:
        ret = list()
        ct = pyudev.Context()
        for dev in ct.list_devices(subsystem='block'):
            if is_dev_matched_by_name(dev, name):
                fs_uuid = dev.get('ID_FS_UUID', '')
                fs_label = dev.get('ID_FS_LABEL', '')
                if dev.get('DEVTYPE', '') == 'partition':
                    device_node = dev.find_parent('block').device_node
                else:
                    device_node = dev.device_node
                ret.append({'device': device_node,
                            'fs_uuid': fs_uuid,
                            'fs_label': fs_label})
        module.exit_json(disks=json.dumps(ret))
    except Exception as e:
        module.exit_json(failed=True, msg=repr(e))

# import module snippets
from ansible.module_utils.basic import *  # noqa
if __name__ == '__main__':
    main()
