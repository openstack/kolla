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
short_description: Return list of devices containing a specfied label
description:
     - This will return a list of all devices with a GPT partition label with
       the name specified.
options:
  partition_name:
    description:
      - Partition name
    required: True
    type: bool
author: Sam Yaple
'''

EXAMPLES = '''
- hosts: ceph-osd
  tasks:
    - name: Return all valid formated devices with the name KOLLA_CEPH_OSD
      ceph_osd_list:
          partition_name: 'KOLLA_CEPH_OSD'
      register: osds
'''

import json
import pyudev

def main():
    module = AnsibleModule(
        argument_spec = dict(
            partition_name = dict(required=True, type='str')
        )
    )
    partition_name = module.params.get('partition_name')

    try:
        ret = list()
        ct = pyudev.Context()
        for dev in ct.list_devices(subsystem='block', DEVTYPE='partition'):
            if dev.get('ID_PART_ENTRY_NAME') == partition_name:
                fs_uuid = dev.get('ID_FS_UUID')
                if not fs_uuid:
                    fs_uuid = ''
                dev_parent = dev.find_parent('block').device_node
                ret.append({'device': dev_parent, 'fs_uuid': fs_uuid})
        module.exit_json(disks=json.dumps(ret))
    except Exception as e:
        module.exit_json(failed=True, msg=repr(e))

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
