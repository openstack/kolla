#!/usr/bin/env python3

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
import re
import shutil
import stat
import sys


# TODO(rhallisey): add docstring.
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

KOLLA_DEFAULTS = "/etc/kolla/defaults"
KOLLA_DEFAULTS_STATE = KOLLA_DEFAULTS + '/' + 'state'


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


class ConfigFileCommandDiffers(ExitingException):
    pass


class StateMismatch(ExitingException):
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
        LOG.info('Copying permissions from %s onto %s', source, dest)
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
            try:
                self._merge_directories(source, dest)
            except OSError:
                # If a source is tried to merge with a read-only mount, it
                # may throw an OSError. Because we don't print the source or
                # dest anywhere, let's catch the exception and log a better
                # message to help with tracking down the issue.
                LOG.error('Unable to merge %s with %s', source, dest)
                raise

    def _cmp_file(self, source, dest):
        # check exist
        if (os.path.exists(source) and
                not os.path.exists(dest)):
            return False
        if (os.path.exists(dest) and
                not os.path.exists(source)):
            return False
        # check content
        with open(source, 'rb') as f1, open(dest, 'rb') as f2:
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
                dest_full_path = os.path.join(dest, os.path.relpath(full_path,
                                                                    source))
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
            if os.path.isdir(source):
                if not self._cmp_dir(source, dest):
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
        if not set(data.keys()) >= required_keys:
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
    def load_from_file():
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
    cmd = '/run_command'
    with open(cmd, 'w+') as f:
        f.write(config['command'])
    # Make sure the generated file is readable by all users
    try:
        os.chmod(cmd, 0o644)
    except OSError:
        LOG.exception('Failed to set permission of %s to 0o644', cmd)


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
        exclude = permission.get('exclude', [])

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

                # Ensure execute bit on directory if read bit is set
                if os.path.isdir(path):
                    if perm & stat.S_IRUSR:
                        perm |= stat.S_IXUSR
                    if perm & stat.S_IRGRP:
                        perm |= stat.S_IXGRP
                    if perm & stat.S_IROTH:
                        perm |= stat.S_IXOTH

                try:
                    os.chmod(path, perm)
                except OSError:
                    LOG.exception('Failed to set permission of %s to %s',
                                  path, perm)

        def handle_exclusion(root, path_suffix):
            full_path = os.path.join(root, path_suffix)
            LOG.debug("Checking for exclusion: %s" % full_path)
            if exclude:
                for exclude_ in exclude:
                    if not re.search(exclude_, full_path):
                        set_perms(full_path, uid, gid, perm)
            else:
                set_perms(full_path, uid, gid, perm)

        for dest in glob.glob(path):
            set_perms(dest, uid, gid, perm)
            if recurse and os.path.isdir(dest):
                for root, dirs, files in os.walk(dest):
                    for dir_ in dirs:
                        handle_exclusion(root, dir_)
                    for file_ in files:
                        handle_exclusion(root, file_)


def get_defaults_state():
    """Retrieve the saved default configuration state from default state file.

    This function creates the directory for Kolla defaults if it does not
    exist, and then attempts to read the current configuration state from
    a JSON file. If the file exists, it reads and returns the content.
    If not, it returns an empty dictionary.

    Simply said, when the container starts for the first time, the state file
    doesn't exist, and it returns an empty dictionary.
    However, if it has already been started before, it will contain the state
    as it was when it first ran.

    Returns:
        dict: The configuration state stored in the Kolla defaults state file.

    Example:
        {
            "/etc/cinder/cinder.conf": {
                "source": "/etc/cinder/cinder.conf",
                "preserve_properties": true,
                "dest": null
            },
            "/etc/apache2/conf-enabled/cinder-wsgi.conf": {
                "source": "/etc/apache2/conf-enabled/cinder-wsgi.conf",
                "preserve_properties": true,
                "dest": null
            },
            "/etc/cinder/cinder_audit_map.conf": {
                "source": "/etc/cinder/cinder_audit_map.conf",
                "preserve_properties": true,
                "dest": "/etc/kolla/defaults/etc/cinder/cinder_audit_map.conf"
            }
        }

        From above example:
        /etc/cinder/cinder.conf didn't exist
        /etc/apache2/conf-enabled/cinder-wsgi.conf didn't exist
        /etc/cinder/cinder_audit_map.conf exists and saved
    """
    os.makedirs(KOLLA_DEFAULTS, exist_ok=True)
    if os.path.exists(KOLLA_DEFAULTS_STATE):
        with open(KOLLA_DEFAULTS_STATE, 'r') as f:
            return json.load(f)
    else:
        return {}


def set_defaults_state(state):
    """Save the provided configuration state to the defaults state file.

    This function writes the provided state (a dictionary) to a JSON file at
    the specified Kolla defaults state location, ensuring that it is properly
    formatted with indentation for readability.

    Args:
        state (dict): The configuration state to save to the Kolla defaults
        state file.
    """
    with open(KOLLA_DEFAULTS_STATE, 'w') as f:
        json.dump(state, f, indent=4)


def remove_or_restore_configs(state):
    """Remove or restore configuration files based on their current state.

    This function iterates over the configuration files in the provided state.
    If the destination is `None`, it removes the file or directory. Otherwise,
    it swaps the source and destination, restoring the configuration file
    by copying it back to its original location.

    Args:
        state (dict): The current default state of configuration files, mapping
        file paths to their source and destination information.
    """
    for k, v in state.items():
        if v['dest'] is None:
            if os.path.exists(k):
                if os.path.isfile(k):
                    os.remove(k)
                else:
                    shutil.rmtree(k)
        else:
            v['source'], v['dest'] = v['dest'], v['source']
            config_file = ConfigFile(**v)
            config_file.copy()


def backup_configs(config, state):
    """Back up new configuration files and update the default state.

    This function processes new configuration files provided in the
    input `config`. For each file, it checks if the destination exists in the
    current state. If not, it backs up the file by copying it to the default
    directory. It then updates the state with the new configuration file's
    information.

    Args:
        config (dict): The input configuration containing a list of config
                       files.
        state (dict): The current default state to be updated with the new
                      config files.
    """
    if 'config_files' in config:
        for data in config['config_files']:
            if data['dest'] in state.keys():
                continue
            src = data['source']
            if data['dest'].endswith('/'):
                dst = data['dest'] + data['source'].split('/')[-1]
            else:
                dst = data['dest']
            default = KOLLA_DEFAULTS + dst
            if os.path.exists(src):
                copy = {'source': dst, 'preserve_properties': True}
                if os.path.exists(dst):
                    copy['dest'] = default
                    if dst not in state:
                        config_file = ConfigFile(**copy)
                        config_file.copy()
                        state[dst] = copy
                else:
                    copy['dest'] = None
                    if dst not in state:
                        state[dst] = copy


def handle_defaults(config):
    """Handle the default config files by copying/removing them as needed.

    This function loads the current default state and manages the configuration
    files. It first processes existing configuration files in the default
    state, either removing or restoring them based on their destination status.
    It then backs up any new configuration files from the input config,
    updating the default state accordingly.

    Args:
        config (dict): A dictionary containing the list of configuration files
        to be handled.
    """
    state = get_defaults_state()
    remove_or_restore_configs(state)
    backup_configs(config, state)
    set_defaults_state(state)


def execute_config_strategy(config):
    config_strategy = os.environ.get("KOLLA_CONFIG_STRATEGY")
    LOG.info("Kolla config strategy set to: %s", config_strategy)
    if config_strategy == "COPY_ALWAYS":
        handle_defaults(config)
        copy_config(config)
        handle_permissions(config)
    elif config_strategy == "COPY_ONCE":
        if os.path.exists('/configured'):
            raise ImmutableConfig(
                "The config strategy prevents copying new configs",
                exit_code=0)
        else:
            handle_defaults(config)
            copy_config(config)
            handle_permissions(config)
            os.mknod('/configured')
    else:
        raise InvalidConfig('KOLLA_CONFIG_STRATEGY is not set properly')


def execute_command_check(config):
    cmd = config.get('command')
    with open("/run_command", "r") as f:
        cmd_running = f.read()
    if cmd != cmd_running:
        msg = "Running command differs. " + cmd + " != " + cmd_running
        raise ConfigFileCommandDiffers(msg)


def execute_config_check(config):
    """Check configuration state consistency and validate config file entries.

    This function compares the current config file destinations from the
    provided config dictionary with those stored in the defaults state file.
    If any destinations are found in the state file but not in the config,
    a StateMismatch exception is raised. These missing files would otherwise
    be restored or removed depending on their backup state.

    After validating consistency, the function performs standard checks on
    each declared configuration file, including content, permissions, and
    ownership validation.

    Args:
        config (dict): The configuration dictionary containing 'config_files'
        entries as expected by Kolla.

    Raises:
        StateMismatch: If there are entries in the defaults state not present
        in the provided config.
    """
    state = get_defaults_state()

    # Build a set of all current destination paths from config.json
    # If the destination is a directory, we append the
    # basename of the source
    current_dests = {
        entry['dest'] if not entry['dest'].endswith('/') else
        os.path.join(entry['dest'], os.path.basename(entry['source']))
        for entry in config.get('config_files', [])
        if entry.get('dest')
    }

    # Detect any paths that are present in the state file but
    # missing from config.json.
    # These would be either restored (if state[dest] has a backup)
    # or removed (if dest is null)
    removed_dests = [
        path for path in state.keys()
        if path not in current_dests
    ]

    if removed_dests:
        raise StateMismatch(
            f"The following config files are tracked in state but missing "
            f"from config.json. "
            f"They would be restored or removed: {sorted(removed_dests)}"
        )

    # Perform the regular content, permissions, and ownership
    # checks on the declared files
    for data in config.get('config_files', []):
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
            execute_command_check(config)
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
