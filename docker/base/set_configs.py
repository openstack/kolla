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

import contextlib
import json
import logging
import os
import pwd
import shutil
import sys

from kazoo import client as kz_client
from kazoo import exceptions as kz_exceptions
from six.moves.urllib import parse


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
        # Verify required keys exist.
        if not data.viewkeys() >= required_keys:
            LOG.error("Config is missing required keys: %s", data)
            sys.exit(1)


def validate_source(data):
    source = data.get('source')

    if is_zk_transport(source):
        with zk_connection(source) as zk:
            exists = zk_path_exists(zk, source)
    else:
        exists = os.path.exists(source)

    if not exists:
        if data.get('optional'):
            LOG.warning("%s does not exist, but is not required", source)
            return False
        else:
            LOG.error("The source to copy does not exist: %s", source)
            sys.exit(1)

    return True


def is_zk_transport(path):
    return path.startswith('zk://') or \
        os.environ.get("KOLLA_ZK_HOSTS") is not None


@contextlib.contextmanager
def zk_connection(url):
    # support an environment and url
    # if url, it should be like this:
    # zk://<address>:<port>/<path>

    zk_hosts = os.environ.get("KOLLA_ZK_HOSTS")
    if zk_hosts is None:
        components = parse.urlparse(url)
        zk_hosts = components.netloc
    zk = kz_client.KazooClient(hosts=zk_hosts)
    zk.start()
    try:
        yield zk
    finally:
        zk.stop()


def zk_path_exists(zk, path):
    try:
        components = parse.urlparse(path)
        zk.get(components.path)
        return True
    except kz_exceptions.NoNodeError:
        return False


def zk_copy_tree(zk, src, dest):
    """Recursively copy contents of url_source into dest."""
    data, stat = zk.get(src)

    if data:
        dest_path = os.path.dirname(dest)
        if not os.path.exists(dest_path):
            LOG.info("Creating dest parent directory: %s", dest_path)
            os.makedirs(dest_path)

        LOG.info("Copying %s to %s", src, dest)
        with open(dest, 'w') as df:
            df.write(data.decode("utf-8"))

    try:
        children = zk.get_children(src)
    except kz_exceptions.NoNodeError:
        return
    for child in children:
        zk_copy_tree(zk, os.path.join(src, child),
                     os.path.join(dest, child))


def copy_files(data):
    dest = data.get('dest')
    source = data.get('source')

    if os.path.exists(dest):
        LOG.info("Removing existing destination: %s", dest)
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

    if is_zk_transport(source):
        with zk_connection(source) as zk:
            components = parse.urlparse(source)
            return zk_copy_tree(zk, components.path, dest)

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
        LOG.info("Copying %s to %s", source, dest)
        shutil.copy(source, dest)
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
            LOG.error("Error while setting permissions for %s: %r",
                      file_, repr(e))
            sys.exit(1)

    dest = data.get('dest')
    owner = data.get('owner')
    perm = int(data.get('perm'), 0)

    # Check for user and group id in the environment.
    try:
        user = pwd.getpwnam(owner)
    except KeyError:
        LOG.error("The specified user does not exist: %s", owner)
        sys.exit(1)

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
            LOG.error('Invalid json for Kolla config')
            sys.exit(1)

    def load_from_file():
        config_file = '/var/lib/kolla/config_files/config.json'
        LOG.info("Loading config file at %s", config_file)

        # Attempt to read config file
        with open(config_file) as f:
            try:
                return json.load(f)
            except ValueError:
                LOG.error("Invalid json file found at %s", config_file)
                sys.exit(1)
            except IOError as e:
                LOG.error("Could not read file %s: %r", config_file, e)
                sys.exit(1)

    config = load_from_env()
    if config is None:
        config = load_from_file()

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
    LOG.debug("Command is: %s", config['command'])
    # The value from the 'command' key will be written to '/run_command'
    with open('/run_command', 'w+') as f:
        f.write(config['command'])


def execute_config_strategy():
    config_strategy = os.environ.get("KOLLA_CONFIG_STRATEGY")
    LOG.info("Kolla config strategy set to: %s", config_strategy)

    if config_strategy == "COPY_ALWAYS":
        load_config()
    elif config_strategy == "COPY_ONCE":
        if os.path.exists('/configured'):
            LOG.info("The config strategy prevents copying new configs")
            sys.exit(0)
        else:
            load_config()
            os.mknod('/configured')
    else:
        LOG.error('KOLLA_CONFIG_STRATEGY is not set properly')
        sys.exit(1)


def main():
    execute_config_strategy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
