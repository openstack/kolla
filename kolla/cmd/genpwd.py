#!/usr/bin/env python

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

import random
import string
import uuid
import yaml


def main():
    # These keys should be random uuids
    uuid_keys = ['ceph_cluster_fsid', 'rbd_secret_uuid']

    # If these keys are None, leave them as None
    blank_keys = ['docker_registry_password']

    # length of password
    length = 40

    with open('/etc/kolla/passwords.yml', 'r') as f:
        passwords = yaml.load(f.read())

    for k, v in passwords.items():
        if v is None:
            if k in blank_keys and v is None:
                continue
            if k in uuid_keys:
                passwords[k] = str(uuid.uuid4())
            else:
                passwords[k] = ''.join([
                    random.SystemRandom().choice(
                        string.ascii_letters + string.digits)
                    for n in range(length)
                ])

    with open('/etc/kolla/passwords.yml', 'w') as f:
        f.write(yaml.dump(passwords, default_flow_style=False))

if __name__ == '__main__':
    main()
