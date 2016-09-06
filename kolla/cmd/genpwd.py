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

import argparse
import os
import random
import string
import uuid
import yaml

from Crypto.PublicKey import RSA


def generate_RSA(bits=4096):
    new_key = RSA.generate(bits, os.urandom)
    private_key = new_key.exportKey("PEM")
    public_key = new_key.publickey().exportKey("OpenSSH")
    return private_key, public_key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--passwords', type=str,
        default=os.path.abspath('/etc/kolla/passwords.yml'),
        help=('Path to the passwords yml file'))

    args = parser.parse_args()
    passwords_file = os.path.expanduser(args.passwords)

    # These keys should be random uuids
    uuid_keys = ['ceph_cluster_fsid', 'rbd_secret_uuid',
                 'gnocchi_project_id', 'gnocchi_resource_id',
                 'gnocchi_user_id']

    # SSH key pair
    ssh_keys = ['kolla_ssh_key', 'nova_ssh_key',
                'keystone_ssh_key', 'bifrost_ssh_key']

    # If these keys are None, leave them as None
    blank_keys = ['docker_registry_password']

    # length of password
    length = 40

    with open(passwords_file, 'r') as f:
        passwords = yaml.safe_load(f.read())

    for k, v in passwords.items():
        if (k in ssh_keys and
                (v is None
                 or v.get('public_key') is None
                 and v.get('private_key') is None)):
            private_key, public_key = generate_RSA()
            passwords[k] = {
                'private_key': private_key,
                'public_key': public_key
            }
            continue
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

    with open(passwords_file, 'w') as f:
        f.write(yaml.dump(passwords, default_flow_style=False))

if __name__ == '__main__':
    main()
