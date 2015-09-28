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

import json
import logging
import os
from pwd import getpwnam
import shutil
import sys


# TODO(rhallisey): add docstring.
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def validate_config(config):
    required_keys = {'source', 'dest', 'owner', 'perm'}

    if 'command' not in config:
        LOG.error('Config is missing required "command" key')
        sys.exit(1)

    # Validate config sections
    for data in config.get('config_files', list()):
        # Verify required keys exist. Only 'source' and 'dest' are
        # required. 'owner' and 'perm' should user system defaults if not
        # specified
        if not data.viewkeys() >= required_keys:
            LOG.error('Config is missing required keys: {}'.format(data))
            sys.exit(1)


def validate_source(data):
    source = data.get('source')

    if not os.path.exists(source):
        if data.get('optional'):
            LOG.warn('{} does not exist, but is not required'.format(source))
            return False
        else:
            LOG.error('The source to copy does not exist: {}'.format(source))
            sys.exit(1)

    return True


def copy_files(data):
    dest = data.get('dest')
    source = data.get('source')

    if os.path.exists(dest):
        LOG.info('Removing existing destination: {}'.format(dest))
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

    if os.path.isdir(source):
        source_path = source
        dest_path = dest
    else:
        source_path = os.path.dirname(source)
        dest_path = os.path.dirname(dest)

    if not os.path.exists(dest_path):
        LOG.info('Creating dest parent directory: {}'.format(dest_path))
        os.makedirs(dest_path)

    if source != source_path:
        # Source is file
        LOG.info('Copying {} to {}'.format(source, dest))
        shutil.copy(source, dest)
    else:
        # Source is a directory
        for src in os.listdir(source_path):
            LOG.info('Copying {} to {}'.format(src, dest_path))
            if os.path.isdir(src):
                shutil.copytree(src, dest_path)
            else:
                shutil.copy(src, dest_path)


def set_permissions(data):
    def set_perms(file_, uid, guid, perm):
        LOG.info('Setting permissions for {}'.format(file_))
        # Give config file proper perms.
        try:
            os.chown(file_, uid, gid)
        except OSError as e:
            LOG.error('While trying to chown {} received error: {}'.format(
                file_, e))
            sys.exit(1)
        try:
            os.chmod(file_, perm)
        except OSError as e:
            LOG.error('While trying to chmod {} received error: {}'.format(
                file_, e))
            sys.exit(1)

    dest = data.get('dest')
    owner = data.get('owner')
    perm = int(data.get('perm'), 0)

    # Check for user and group id in the environment.
    try:
        uid = getpwnam(owner).pw_uid
    except KeyError:
        LOG.error('The specified user does not exist: {}'.format(owner))
        sys.exit(1)
    try:
        gid = getpwnam(owner).pw_gid
    except KeyError:
        LOG.error('The specified group does not exist: {}'.format(owner))
        sys.exit(1)

    # Set permissions on the top level dir or file
    set_perms(dest, uid, gid, perm)
    if os.path.isdir(dest):
        # Recursively set permissions
        for root, dirs, files in os.walk(dest):
            for dir_ in dirs:
                set_perms(os.path.join(root, dir_), uid, gid, perm)
            for file_ in files:
                set_perms(os.path.join(root, file_), uid, gid, perm)


def load_config():
    config_file = '/opt/kolla/config_files/config.json'
    LOG.info('Loading config file at {}'.format(config_file))

    # Attempt to read config file
    with open(config_file) as f:
        try:
            config = json.load(f)
        except ValueError:
            LOG.error('Invalid json file found at {}'.format(config_file))
            sys.exit(1)
        except IOError as e:
            LOG.error('Could not read file {}. Failed with error {}'.format(
                config_file, e))
            sys.exit(1)

    LOG.info('Validating config file')
    validate_config(config)

    if 'config_files' in config:
        LOG.info('Copying service configuration files')
        for data in config['config_files']:
            if validate_source(data):
                copy_files(data)
                set_permissions(data)
    else:
        LOG.debug('No files to copy found in config')

    LOG.info('Writing out command to execute')
    LOG.debug('Command is: {}'.format(config['command']))
    # The value from the 'command' key will be written to '/run_command'
    with open('/run_command', 'w+') as f:
        f.write(config['command'])


def execute_config_strategy():
    try:
        config_strategy = os.environ.get("KOLLA_CONFIG_STRATEGY")
        LOG.info('Kolla config strategy set to: {}'.format(config_strategy))
    except KeyError:
        LOG.error("KOLLA_CONFIG_STRATEGY is not set properly.")
        sys.exit(1)

    if config_strategy == "COPY_ALWAYS":
        load_config()
    elif config_strategy == "COPY_ONCE":
        if os.path.exists('/configured'):
            LOG.info("The config strategy prevents copying new configs")
            sys.exit(0)
        else:
            load_config()
            f = open('/configured', 'w+')
            f.close()
    else:
        LOG.error('KOLLA_CONFIG_STRATEGY is not set properly')
        sys.exit(1)


def main():
    execute_config_strategy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
