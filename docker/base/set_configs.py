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


class UserNotFound(ExitingException):
    pass


class ConfigFileBadState(ExitingException):
    pass


class ConfigFile(object):

    def __init__(self, source, dest, owner=None, perm=None, optional=False,
                 preserve_properties=False, merge=False):
        self.source = source
        self.dest = dest
        self.owner = owner
        self.perm = perm
        self.optional = optional
        self.merge = merge
        self.preserve_properties = preserve_properties

    def __str__(self):
        return '<ConfigFile source:"{}" dest:"{}">'.format(self.source,
                                                           self.dest)

    def _copy_file(self, source, dest):
        self._delete_path(dest)
        # dest endswith / means copy the <source> to <dest> folder
        LOG.info('Copying %s to %s', source, dest)
        if self.merge and self.preserve_properties and os.path.islink(source):
            link_target = os.readlink(source)
            os.symlink(link_target, dest)
        else:
            shutil.copy(source, dest)
            self._set_properties(source, dest)

    def _merge_directories(self, source, dest):
        if os.path.isdir(source):
            if os.path.lexists(dest) and not os.path.isdir(dest):
                self._delete_path(dest)
            if not os.path.isdir(dest):
                LOG.info('Creating directory %s', dest)
                os.makedirs(dest)
            self._set_properties(source, dest)

            dir_content = os.listdir(source)
            for to_copy in dir_content:
                self._merge_directories(os.path.join(source, to_copy),
                                        os.path.join(dest, to_copy))
        else:
            self._copy_file(source, dest)

    def _delete_path(self, path):
        if not os.path.lexists(path):
            return
        LOG.info('Deleting %s', path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def _create_parent_dirs(self, path):
        parent_path = os.path.dirname(path)
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)

    def _set_properties(self, source, dest):
        if self.preserve_properties:
            self._set_properties_from_file(source, dest)
        else:
            self._set_properties_from_conf(dest)

    def _set_properties_from_file(self, source, dest):
        shutil.copystat(source, dest)
        stat = os.stat(source)
        os.chown(dest, stat.st_uid, stat.st_gid)

    def _set_properties_from_conf(self, path):
        config = {'permissions':
                  [{'owner': self.owner, 'path': path, 'perm': self.perm}]}
        handle_permissions(config)

    def copy(self):

        sources = glob.glob(self.source)

        if not self.optional and not sources:
            raise MissingRequiredSource('%s file is not found' % self.source)
        # skip when there is no sources and optional
        elif self.optional and not sources:
            return

        for source in sources:
            dest = self.dest
            # dest endswith / means copy the <source> into <dest> folder,
            # otherwise means copy the source to dest
            if dest.endswith(os.sep):
                dest = os.path.join(dest, os.path.basename(source))
            if not self.merge:
                self._delete_path(dest)
            self._create_parent_dirs(dest)
            self._merge_directories(source, dest)

    def _cmp_file(self, source, dest):
        # check exsit
        if (os.path.exists(source) and
                not self.optional and
                not os.path.exists(dest)):
            return False
        # check content
        with open(source) as f1, open(dest) as f2:
            if f1.read() != f2.read():
                LOG.error('The content of source file(%s) and'
                          ' dest file(%s) are not equal.', source, dest)
                return False
        # check perm
        file_stat = os.stat(dest)
        actual_perm = oct(file_stat.st_mode)[-4:]
        if self.perm != actual_perm:
            LOG.error('Dest file does not have expected perm: %s, actual: %s',
                      self.perm, actual_perm)
            return False
        # check owner
        desired_user, desired_group = user_group(self.owner)
        actual_user = pwd.getpwuid(file_stat.st_uid)
        if actual_user.pw_name != desired_user:
            LOG.error('Dest file does not have expected user: %s,'
                      ' actual: %s ', desired_user, actual_user.pw_name)
            return False
        actual_group = grp.getgrgid(file_stat.st_gid)
        if actual_group.gr_name != desired_group:
            LOG.error('Dest file does not have expected group: %s,'
                      ' actual: %s ', desired_group, actual_group.gr_name)
            return False
        return True

    def _cmp_dir(self, source, dest):
        for root, dirs, files in os.walk(source):
            for dir_ in dirs:
                full_path = os.path.join(root, dir_)
                dest_full_path = os.path.join(dest, os.path.relpath(source,
                                                                    full_path))
                dir_stat = os.stat(dest_full_path)
                actual_perm = oct(dir_stat.st_mode)[-4:]
                if self.perm != actual_perm:
                    LOG.error('Dest dir does not have expected perm: %s,'
                              ' actual %s', self.perm, actual_perm)
                    return False
            for file_ in files:
                full_path = os.path.join(root, file_)
                dest_full_path = os.path.join(dest, os.path.relpath(source,
                                                                    full_path))
                if not self._cmp_file(full_path, dest_full_path):
                    return False
        return True

    def check(self):
        bad_state_files = []
        sources = glob.glob(self.source)

        if not sources and not self.optional:
            raise MissingRequiredSource('%s file is not found' % self.source)
        elif self.optional and not sources:
            return

        for source in sources:
            dest = self.dest
            # dest endswith / means copy the <source> into <dest> folder,
            # otherwise means copy the source to dest
            if dest.endswith(os.sep):
                dest = os.path.join(dest, os.path.basename(source))
            if os.path.isdir(source) and not self._cmp_dir(source, dest):
                bad_state_files.append(source)
            elif not self._cmp_file(source, dest):
                bad_state_files.append(source)
        if len(bad_state_files) != 0:
            msg = 'Following files are in bad state: %s' % bad_state_files
            raise ConfigFileBadState(msg)


def validate_config(config):
    required_keys = {'source', 'dest'}

    if 'command' not in config:
        raise InvalidConfig('Config is missing required "command" key')

    # Validate config sections
    for data in config.get('config_files', list()):
        # Verify required keys exist.
        if not data.viewkeys() >= required_keys:
            message = 'Config is missing required keys: %s' % required_keys
            raise InvalidConfig(message)
        if ('owner' not in data or 'perm' not in data) \
                and not data.get('preserve_properties', False):
            raise InvalidConfig(
                'Config needs preserve_properties or owner and perm')


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
            config_file = ConfigFile(**data)
            config_file.copy()
    else:
        LOG.debug('No files to copy found in config')

    LOG.info('Writing out command to execute')
    LOG.debug("Command is: %s", config['command'])
    # The value from the 'command' key will be written to '/run_command'
    with open('/run_command', 'w+') as f:
        f.write(config['command'])


def user_group(owner):
    if ':' in owner:
        user, group = owner.split(':', 1)
        if not group:
            group = user
    else:
        user, group = owner, owner
    return user, group


def handle_permissions(config):
    for permission in config.get('permissions', list()):
        path = permission.get('path')
        owner = permission.get('owner')
        recurse = permission.get('recurse', False)
        perm = permission.get('perm')

        desired_user, desired_group = user_group(owner)
        uid = pwd.getpwnam(desired_user).pw_uid
        gid = grp.getgrnam(desired_group).gr_gid

        def set_perms(path, uid, gid, perm):
            LOG.info('Setting permission for %s', path)
            if not os.path.exists(path):
                LOG.warning('%s does not exist', path)
                return

            try:
                os.chown(path, uid, gid)
            except OSError:
                LOG.exception('Failed to change ownership of %s to %s:%s',
                              path, uid, gid)

            if perm:
                # NOTE(Jeffrey4l): py3 need '0oXXX' format for octal literals,
                # and py2 support such format too.
                if len(perm) == 4 and perm[1] != 'o':
                    perm = ''.join([perm[:1], 'o', perm[1:]])
                perm = int(perm, base=0)

                try:
                    os.chmod(path, perm)
                except OSError:
                    LOG.exception('Failed to set permission of %s to %s',
                                  path, perm)

        for dest in glob.glob(path):
            set_perms(dest, uid, gid, perm)
            if recurse and os.path.isdir(dest):
                for root, dirs, files in os.walk(dest):
                    for dir_ in dirs:
                        set_perms(os.path.join(root, dir_), uid, gid, perm)
                    for file_ in files:
                        set_perms(os.path.join(root, file_), uid, gid, perm)


def execute_config_strategy(config):
    config_strategy = os.environ.get("KOLLA_CONFIG_STRATEGY")
    LOG.info("Kolla config strategy set to: %s", config_strategy)
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


def execute_config_check(config):
    for data in config['config_files']:
        config_file = ConfigFile(**data)
        config_file.check()


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--check',
                            action='store_true',
                            required=False,
                            help='Check whether the configs changed')
        args = parser.parse_args()
        config = load_config()

        if args.check:
            execute_config_check(config)
        else:
            execute_config_strategy(config)
    except ExitingException as e:
        LOG.error("%s: %s", e.__class__.__name__, e)
        return e.exit_code
    except Exception:
        LOG.exception('Unexpected error:')
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
