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

# This is a stripped down version of an ansible module I wrote in Yaodu to
# achieve the same goals we have for Kolla. I have relicensed it for Kolla
# https://github.com/SamYaple/yaodu/blob/master/ansible/library/bslurp

# Basically this module will fetch the admin and mon keyrings as well as the
# monmap file. It then hashes the content, compresses them, and finally it
# converts them to base64 to be safely transported around with ansible

import base64
import hashlib
import json
import os
import sys
import zlib


def json_exit(msg=None, failed=False, changed=False):
    if type(msg) is not dict:
        msg = {'msg': str(msg)}
    msg.update({'failed': failed, 'changed': changed})
    print(json.dumps(msg))
    sys.exit()


def read_file(filename):
    filename_path = os.path.join('/etc/ceph', filename)

    if not os.path.exists(filename_path):
        json_exit("file not found: {}".format(filename_path), failed=True)
    if not os.access(filename_path, os.R_OK):
        json_exit("file not readable: {}".format(filename_path), failed=True)

    with open(filename_path, 'rb') as f:
        raw_data = f.read()

    return {'content': base64.b64encode(zlib.compress(raw_data)),
            'sha1': hashlib.sha1(raw_data).hexdigest(),
            'filename': filename}


def main():
    admin_keyring = 'ceph.client.admin.keyring'
    mon_keyring = 'ceph.client.mon.keyring'
    rgw_keyring = 'ceph.client.radosgw.keyring'
    monmap = 'ceph.monmap'

    files = [admin_keyring, mon_keyring, rgw_keyring, monmap]
    json_exit({filename: read_file(filename) for filename in files})


if __name__ == '__main__':
    main()
