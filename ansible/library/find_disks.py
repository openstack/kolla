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

import sys
import subprocess


def main():
    module = AnsibleModule(
        argument_spec = dict(
            partition_name = dict(required=True, type='str')
        )
    )

    partition_name = module.params.get('partition_name')

    try:
        # This should all really be done differently. Unfortunately there is no
        # decent python library for dealing with disks like we need to here.
        disks = subprocess.check_output("parted -l", shell=True).split('\n')
        ret = list()

        for line in disks:
            d = line.split(' ')
            if d[0] == 'Disk' and d[1] != 'Flags:':
                dev = d[1][:-1]

            if line.find(partition_name) != -1:
                # This process returns an error code when no results return
                # We can ignore that, it is safe
                p = subprocess.Popen("blkid " + dev + "*", shell=True, stdout=subprocess.PIPE)
                blkid_out = p.communicate()[0]
                # The dev doesn't need to have a uuid, will be '' otherwise
                if ' UUID=' in blkid_out:
                    fs_uuid = blkid_out.split(' UUID="')[1].split('"')[0]
                else:
                    fs_uuid = ''
                ret.append({'device': dev, 'fs_uuid': fs_uuid})

        module.exit_json(disks=ret)
    except Exception as e:
        module.exit_json(failed=True, msg=repr(e))

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
