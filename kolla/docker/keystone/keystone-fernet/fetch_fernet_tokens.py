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

# Basically this module will fetch the fernet tokens and compare them to the
# required time constrains to determine whether the host needs to resync with
# other nodes in the cluster.
import argparse
from datetime import datetime
from datetime import timedelta
import json
import os
import sys

# Adding nosec since this fails bandit B105, 'Possible hardcoded password'.
TOKEN_PATH = '/etc/keystone/fernet-keys'  # nosec


def json_exit(msg=None, failed=False, changed=False):
    if type(msg) is not dict:
        msg = {'msg': str(msg)}
    msg.update({'failed': failed, 'changed': changed})
    print(json.dumps(msg))
    sys.exit()


def has_file(filename_path):
    if not os.path.exists(filename_path):
        return False
    return True


def num_tokens():
    _, _, files = next(os.walk(TOKEN_PATH))
    return len(files)


def tokens_populated(expected):
    return num_tokens() >= int(expected)


def token_stale(seconds, filename='0'):
    max_token_age = datetime.now() - timedelta(seconds=int(seconds))
    filename_path = os.path.join(TOKEN_PATH, filename)

    if not has_file(filename_path):
        return True
    modified_date = datetime.fromtimestamp(os.path.getmtime(filename_path))
    return modified_date < max_token_age


def main():
    parser = argparse.ArgumentParser(description='''Checks to see if a fernet
        token no older than a desired time.''')
    parser.add_argument('-t', '--time',
                        help='Time in seconds for a token rotation',
                        required=True)
    parser.add_argument('-f', '--filename',
                        help='Filename of token to check',
                        default='0')
    parser.add_argument('-n', '--number',
                        help='Minimum number of tokens that should exist',
                        required=True)
    args = parser.parse_args()

    json_exit({
        'populated': tokens_populated(args.number),
        'update_required': token_stale(args.time, args.filename),
    })


if __name__ == '__main__':
    main()
