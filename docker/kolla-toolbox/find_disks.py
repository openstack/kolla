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
  use_udev:
    description:
      - When True, use Linux udev to read disk info such as partition labels,
        uuid, etc.  Some older host operating systems have issues using udev to
        get the info this module needs. Set to False to fall back to more low
        level commands such as blkid to retrieve this information. Most users
        should not need to change this.
    default: True
    required: False
    type: bool
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
import re
import subprocess  # nosec


PREFERRED_DEVICE_LINK_ORDER = [
    '/dev/disk/by-uuid',
    '/dev/disk/by-partuuid',
    '/dev/disk/by-parttypeuuid',
    '/dev/disk/by-label',
    '/dev/disk/by-partlabel'
]


def get_id_part_entry_name(dev, use_udev):
    if use_udev:
        dev_name = dev.get('ID_PART_ENTRY_NAME', '')
    else:
        part = re.sub(r'.*[^\d]', '', dev.device_node)
        parent = dev.find_parent('block').device_node
        # NOTE(Mech422): Need to use -i as -p truncates the partition name
        out = subprocess.Popen(['/usr/sbin/sgdisk', '-i', part,  # nosec
                                parent],
                               stdout=subprocess.PIPE).communicate()
        match = re.search(r'Partition name: \'(\w+)\'', out[0])
        if match:
            dev_name = match.group(1)
        else:
            dev_name = ''
    return dev_name


def get_id_fs_uuid(dev, use_udev):
    if use_udev:
        id_fs_uuid = dev.get('ID_FS_UUID', '')
    else:
        out = subprocess.Popen(['/usr/sbin/blkid', '-o', 'export',  # nosec
                                dev.device_node],
                               stdout=subprocess.PIPE).communicate()
        match = re.search(r'\nUUID=([\w-]+)', out[0])
        if match:
            id_fs_uuid = match.group(1)
        else:
            id_fs_uuid = ''
    return id_fs_uuid


def is_dev_matched_by_name(dev, name, mode, use_udev):
    if dev.get('DEVTYPE', '') == 'partition':
        dev_name = get_id_part_entry_name(dev, use_udev)
    else:
        dev_name = dev.get('ID_FS_LABEL', '')

    if mode == 'strict':
        return dev_name == name
    elif mode == 'prefix':
        return dev_name.startswith(name)
    else:
        return False


def find_disk(ct, name, match_mode, use_udev):
    for dev in ct.list_devices(subsystem='block'):
        if is_dev_matched_by_name(dev, name, match_mode, use_udev):
            yield dev


def get_device_link(dev):
    for preferred_link in PREFERRED_DEVICE_LINK_ORDER:
        for link in dev.device_links:
            if link.startswith(preferred_link):
                return link
    return dev.device_node


def extract_disk_info(ct, dev, name, use_udev):
    if not dev:
        return
    kwargs = dict()
    kwargs['fs_uuid'] = get_id_fs_uuid(dev, use_udev)
    kwargs['fs_label'] = dev.get('ID_FS_LABEL', '')
    if dev.get('DEVTYPE', '') == 'partition':
        kwargs['partition_label'] = name
        kwargs['device'] = dev.find_parent('block').device_node
        kwargs['partition'] = dev.device_node
        kwargs['partition_num'] = \
            re.sub(r'.*[^\d]', '', dev.device_node)
        if is_dev_matched_by_name(dev, name, 'strict', use_udev):
            kwargs['external_journal'] = False
            # NOTE(jeffrey4l): this is only used for bootstrap osd stage and
            # there is no journal partion at all. So it is OK to use
            # device_node directly.
            kwargs['journal'] = dev.device_node[:-1] + '2'
            kwargs['journal_device'] = kwargs['device']
            kwargs['journal_num'] = 2
        else:
            kwargs['external_journal'] = True
            journal_name = get_id_part_entry_name(dev, use_udev) + '_J'
            for journal in find_disk(ct, journal_name, 'strict', use_udev):
                kwargs['journal'] = get_device_link(journal)
                kwargs['journal_device'] = \
                    journal.find_parent('block').device_node
                kwargs['journal_num'] = \
                    re.sub(r'.*[^\d]', '', journal.device_node)
                break
            if 'journal' not in kwargs:
                # NOTE(SamYaple): Journal not found, not returning info
                return
    else:
        kwargs['device'] = dev.device_node
    yield kwargs


def extract_disk_info_bs(ct, dev, name, use_udev):
    if not dev:
        return
    kwargs = dict(bs_blk_label='', bs_blk_device='', bs_db_label='',
                  bs_db_device='', bs_wal_label='', bs_wal_device='',
                  bs_wal_partition_num='', bs_db_partition_num='',
                  bs_blk_partition_num='', partition='', partition_label='',
                  partition_num='', device='', partition_usage='')
    kwargs['fs_uuid'] = get_id_fs_uuid(dev, use_udev)
    kwargs['fs_label'] = dev.get('ID_FS_LABEL', '')

    if dev.get('DEVTYPE', '') == 'partition':
        actual_name = get_id_part_entry_name(dev, use_udev)

        if (('BOOTSTRAP_BS' in name or 'BSDATA' in name)
                and name in actual_name):
            if '_BS_B' in actual_name:
                kwargs['partition_usage'] = 'block'
                kwargs['bs_blk_partition_num'] = \
                    re.sub(r'.*[^\d]', '', dev.device_node)
                kwargs['bs_blk_device'] = dev.find_parent('block').device_node
                kwargs['bs_blk_label'] = actual_name
                return kwargs
            if '_BS_D' in actual_name:
                kwargs['partition_usage'] = 'block.db'
                kwargs['bs_db_partition_num'] = \
                    re.sub(r'.*[^\d]', '', dev.device_node)
                kwargs['bs_db_device'] = dev.find_parent('block').device_node
                kwargs['bs_db_label'] = actual_name
                return kwargs
            if '_BS_W' in actual_name:
                kwargs['partition_usage'] = 'block.wal'
                kwargs['bs_wal_partition_num'] = \
                    re.sub(r'.*[^\d]', '', dev.device_node)
                kwargs['bs_wal_device'] = dev.find_parent('block').device_node
                kwargs['bs_wal_label'] = actual_name
                return kwargs
            if '_BS' in actual_name:
                kwargs['partition_usage'] = 'osd'
                kwargs['partition'] = dev.find_parent('block').device_node
                kwargs['partition_label'] = actual_name
                kwargs['partition_num'] = \
                    re.sub(r'.*[^\d]', '', dev.device_node)
                kwargs['device'] = dev.find_parent('block').device_node
                return kwargs
    return 0


def nb_of_osd(disks):
    osd_info = dict()
    osd_info['block_label'] = list()
    nb_of_osds = 0
    for item in disks:
        if item['partition_usage'] == 'osd':
            osd_info['block_label'].append(item['partition_label'])
            nb_of_osds += 1
    osd_info['nb_of_osd'] = nb_of_osds
    return osd_info


def combine_info(disks):
    info = list()
    osds = nb_of_osd(disks)
    osd_id = 0
    while osd_id < osds['nb_of_osd']:
        final = dict()
        idx = 0
        idx_osd = idx_blk = idx_wal = idx_db = -1
        for item in disks:
            if (item['partition_usage'] == 'osd' and
                    item['partition_label'] == osds['block_label'][osd_id]):
                idx_osd = idx
            elif (item['partition_usage'] == 'block' and
                    item['bs_blk_label'] ==
                    osds['block_label'][osd_id].replace('_BS', '_BS_B')):
                idx_blk = idx
            elif (item['partition_usage'] == 'block.wal' and
                    item['bs_wal_label'] ==
                    osds['block_label'][osd_id].replace('_BS', '_BS_W')):
                idx_wal = idx
            elif (item['partition_usage'] == 'block.db' and
                    item['bs_db_label'] ==
                    osds['block_label'][osd_id].replace('_BS', '_BS_D')):
                idx_db = idx
            idx = idx + 1

        # write the information of block.db and block.wal to block item
        # if block.db and block.wal are found
        if idx_blk != -1:
            disks[idx_osd]['bs_blk_device'] = disks[idx_blk]['bs_blk_device']
            disks[idx_osd]['bs_blk_label'] = disks[idx_blk]['bs_blk_label']
            disks[idx_osd]['bs_blk_partition_num'] = \
                disks[idx_blk]['bs_blk_partition_num']
            disks[idx_blk]['partition_usage'] = ''
        if idx_wal != -1:
            disks[idx_osd]['bs_wal_device'] = disks[idx_wal]['bs_wal_device']
            disks[idx_osd]['bs_wal_partition_num'] = \
                disks[idx_wal]['bs_wal_partition_num']
            disks[idx_osd]['bs_wal_label'] = disks[idx_wal]['bs_wal_label']
            disks[idx_wal]['partition_usage'] = ''
        if idx_db != -1:
            disks[idx_osd]['bs_db_device'] = disks[idx_db]['bs_db_device']
            disks[idx_osd]['bs_db_partition_num'] = \
                disks[idx_db]['bs_db_partition_num']
            disks[idx_osd]['bs_db_label'] = disks[idx_db]['bs_db_label']
            disks[idx_db]['partition_usage'] = ''

        final['fs_uuid'] = disks[idx_osd]['fs_uuid']
        final['fs_label'] = disks[idx_osd]['fs_label']
        final['bs_blk_device'] = disks[idx_osd]['bs_blk_device']
        final['bs_blk_label'] = disks[idx_osd]['bs_blk_label']
        final['bs_blk_partition_num'] = disks[idx_osd]['bs_blk_partition_num']
        final['bs_db_device'] = disks[idx_osd]['bs_db_device']
        final['bs_db_partition_num'] = disks[idx_osd]['bs_db_partition_num']
        final['bs_db_label'] = disks[idx_osd]['bs_db_label']
        final['bs_wal_device'] = disks[idx_osd]['bs_wal_device']
        final['bs_wal_partition_num'] = disks[idx_osd]['bs_wal_partition_num']
        final['bs_wal_label'] = disks[idx_osd]['bs_wal_label']
        final['device'] = disks[idx_osd]['device']
        final['partition'] = disks[idx_osd]['partition']
        final['partition_label'] = disks[idx_osd]['partition_label']
        final['partition_num'] = disks[idx_osd]['partition_num']
        final['external_journal'] = False
        final['journal'] = ''
        final['journal_device'] = ''
        final['journal_num'] = 0

        info.append(final)
        disks[idx_osd]['partition_usage'] = ''
        osd_id += 1

    return info


def main():
    argument_spec = dict(
        match_mode=dict(required=False, choices=['strict', 'prefix'],
                        default='strict'),
        name=dict(aliases=['partition_name'], required=True, type='str'),
        use_udev=dict(required=False, default=True, type='bool')
    )
    module = AnsibleModule(argument_spec)
    match_mode = module.params.get('match_mode')
    name = module.params.get('name')
    use_udev = module.params.get('use_udev')

    try:
        ret = list()
        ct = pyudev.Context()
        for dev in find_disk(ct, name, match_mode, use_udev):
            if '_BSDATA' in name:
                info = extract_disk_info_bs(ct, dev, name, use_udev)
                if info:
                    ret.append(info)
            elif '_BS' in name:
                info = extract_disk_info_bs(ct, dev, name, use_udev)
                if info:
                    ret.append(info)

                info = extract_disk_info_bs(ct, dev,
                                            name.replace('_BS', '_BS_B'),
                                            use_udev)
                if info:
                    ret.append(info)

                info = extract_disk_info_bs(ct, dev,

                                            name.replace('_BS', '_BS_W'),
                                            use_udev)
                if info:
                    ret.append(info)

                info = extract_disk_info_bs(ct, dev,
                                            name.replace('_BS', '_BS_D'),
                                            use_udev)
                if info:
                    ret.append(info)
            else:
                for info in extract_disk_info(ct, dev, name, use_udev):
                    if info:
                        ret.append(info)

        if '_BS' in name and len(ret) > 0:
            ret = combine_info(ret)

        module.exit_json(disks=json.dumps(ret))
    except Exception as e:
        module.exit_json(failed=True, msg=repr(e))

# import module snippets
from ansible.module_utils.basic import *  # noqa
if __name__ == '__main__':
    main()
