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
import glob
import grp
import json
import logging
import os
import pwd
import shutil
import sys


# TODO(rhallisey): add docstring.
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class ExitingException(Exception):
    def __init__(self, message, exit_code=1):
        super(ExitingException, self).__init__(message)
        self.exit_code = exit_code


class ImmutableConfig(ExitingException):
    pass


class InvalidConfig(ExitingException):
    pass


class MissingRequiredSource(ExitingException):
    pass


class PermissionsError(ExitingException):
    pass


class UserNotFound(ExitingException):
    pass


class DifferentPermissions(ExitingException):
    pass


class DifferentUser(ExitingException):
    pass


class RequiredFileNotFound(ExitingException):
    pass


class ContentDifferent(ExitingException):
    pass


def validate_config(config):
    config_files_required_keys = {'source', 'dest', 'owner', 'perm'}
    permissions_required_keys = {'path', 'owner'}

    if 'command' not in config:
        raise InvalidConfig('Config is missing required "command" key')

    # Validate config sections
    for data in config.get('config_files', list()):
        # Verify required keys exist.
        if not data.viewkeys() >= config_files_required_keys:
            raise InvalidConfig(
                "Config is missing required keys: %s" % data)
    for data in config.get('permissions', list()):
        if not data.viewkeys() >= permissions_required_keys:
            raise InvalidConfig("Config is missing required keys: %s" % data)


def validate_source(data):
    source = data.get('source')

    # Only check existence if no wildcard found
    if '*' not in source:
        if not os.path.exists(source):
            if data.get('optional'):
                LOG.info("%s does not exist, but is not required", source)
                return False
            else:
                raise MissingRequiredSource(
                    "The source to copy does not exist: %s" % source)

    return True


def copy_files(data):
    dest = data.get('dest')
    source = data.get('source')

    if os.path.exists(dest):
        LOG.info("Removing existing destination: %s", dest)
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
        LOG.info("Creating dest parent directory: %s", dest_path)
        os.makedirs(dest_path)

    if source != source_path:
        # Source is file
        for file in glob.glob(source):
            LOG.info("Copying %s to %s", file, dest)
            shutil.copy(file, dest)
    else:
        # Source is a directory
        for src in os.listdir(source_path):
            LOG.info("Copying %s to %s",
                     os.path.join(source_path, src), dest_path)

            if os.path.isdir(os.path.join(source_path, src)):
                shutil.copytree(os.path.join(source_path, src), dest_path)
            else:
                shutil.copy(os.path.join(source_path, src), dest_path)


def set_permissions(data):
    def set_perms(file_, uid, guid, perm):
        LOG.info("Setting permissions for %s", file_)
        # Give config file proper perms.
        try:
            os.chown(file_, uid, gid)
            os.chmod(file_, perm)
        except OSError as e:
            raise PermissionsError(
                "Error while setting permissions for %s: %r" % (file_,
                                                                repr(e)))

    dest = data.get('dest')
    owner = data.get('owner')
    perm = int(data.get('perm'), 0)

    # Check for user and group id in the environment.
    try:
        user = pwd.getpwnam(owner)
    except KeyError:
        raise UserNotFound("The specified user does not exist: %s" % owner)

    uid = user.pw_uid
    gid = user.pw_gid

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
    def load_from_env():
        config_raw = os.environ.get("KOLLA_CONFIG")
        if config_raw is None:
            return None

        # Attempt to read config
        try:
            return json.loads(config_raw)
        except ValueError:
            raise InvalidConfig('Invalid json for Kolla config')

    def load_from_file():
        config_file = os.environ.get("KOLLA_CONFIG_FILE")
        if not config_file:
            config_file = '/var/lib/kolla/config_files/config.json'
        LOG.info("Loading config file at %s", config_file)

        # Attempt to read config file
        with open(config_file) as f:
            try:
                return json.load(f)
            except ValueError:
                raise InvalidConfig(
                    "Invalid json file found at %s" % config_file)
            except IOError as e:
                raise InvalidConfig(
                    "Could not read file %s: %r" % (config_file, e))

    config = load_from_env()
    if config is None:
        config = load_from_file()

    LOG.info('Validating config file')
    validate_config(config)
    return config


def copy_config(config):
    if 'config_files' in config:
        LOG.info('Copying service configuration files')
        for data in config['config_files']:
            if validate_source(data):
                copy_files(data)
                set_permissions(data)
    else:
        LOG.debug('No files to copy found in config')

    LOG.info('Writing out command to execute')
    LOG.debug("Command is: %s", config['command'])
    # The value from the 'command' key will be written to '/run_command'
    with open('/run_command', 'w+') as f:
        f.write(config['command'])


def handle_permissions(config):
    for permission in config.get('permissions', list()):
        path = permission.get('path')
        owner = permission.get('owner')
        recurse = permission.get('recurse', False)

        if ':' in owner:
            user, group = owner.split(':', 1)
            if not group:
                group = user
        else:
            user, group = owner, owner

        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid

        def set_perms(path, uid, gid):
            LOG.info('Setting permission for %s', path)
            os.chown(path, uid, gid)

        for dest in glob.glob(path):
            set_perms(dest, uid, gid)
            if recurse and os.path.isdir(dest):
                for root, dirs, files in os.walk(dest):
                    for dir_ in dirs:
                        set_perms(os.path.join(root, dir_), uid, gid)
                    for file_ in files:
                        set_perms(os.path.join(root, file_), uid, gid)


def execute_config_strategy():
    config_strategy = os.environ.get("KOLLA_CONFIG_STRATEGY")
    LOG.info("Kolla config strategy set to: %s", config_strategy)
    config = load_config()

    if config_strategy == "COPY_ALWAYS":
        copy_config(config)
        handle_permissions(config)
    elif config_strategy == "COPY_ONCE":
        if os.path.exists('/configured'):
            raise ImmutableConfig(
                "The config strategy prevents copying new configs",
                exit_code=0)
        else:
            copy_config(config)
            handle_permissions(config)
            os.mknod('/configured')
    else:
        raise InvalidConfig('KOLLA_CONFIG_STRATEGY is not set properly')


def execute_config_check():
    config = load_config()
    for config_file in config.get('config_files', {}):
        source = config_file.get('source')
        dest = config_file.get('dest')
        perm = config_file.get('perm')
        owner = config_file.get('owner')
        optional = config_file.get('optional', False)
        if not os.path.exists(dest):
            if optional:
                LOG.info('Dest file does not exist, but is optional: %s',
                         dest)
                return
            else:
                raise RequiredFileNotFound(
                    'Dest file does not exist and is: %s' % dest)
        # check content
        with open(source) as fp1, open(dest) as fp2:
            if fp1.read() != fp2.read():
                raise ContentDifferent(
                    'The content of source file(%s) and'
                    ' dest file(%s) are not equal.' % (source, dest))
        # check perm
        file_stat = os.stat(dest)
        actual_perm = oct(file_stat.st_mode)[-4:]
        if perm != actual_perm:
            raise DifferentPermissions(
                'Dest file does not have expected perm: %s, actual: %s'
                % (perm, actual_perm))
        # check owner
        actual_user = pwd.getpwuid(file_stat.st_uid)
        if actual_user.pw_name != owner:
            raise DifferentUser(
                'Dest file does not have expected user: %s, actual: %s '
                % (owner, actual_user.pw_name))
    LOG.info('The config files are in the expected state')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',
                        action='store_true',
                        required=False,
                        help='Check whether the configs changed')
    conf = parser.parse_args()

    if conf.check:
        execute_config_check()
    else:
        execute_config_strategy()


if __name__ == "__main__":
    _exit_code = 0
    try:
        main()
    except ExitingException as e:
        LOG.error("%s: %s" % e.__class__.__name__, e)
        _exit_code = e.exit_code
    except Exception:
        LOG.exception('Unexpected error:')
        _exit_code = 2
    sys.exit(_exit_code)
