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


def json_key_validation(json_file):
    valid_keys = ['source', 'dest', 'owner', 'perm']

    # 'command' is not present in the json file
    if json_file.get('command') is None:
        LOG.error('command was never specified in your json file. Command '
                  'is what your container will execute upon start.')
        sys.exit(1)

    # Check for valid keys
    for data in json_file.get('config_files'):
        key_not_found = ''
        for valid_key in valid_keys:
            if valid_key not in data.keys():
                key_not_found += valid_key + ' '

        if key_not_found is not '':
            LOG.error('JSON data "%s" is missing keys "%s"'
                      % (data.keys(), key_not_found))
            sys.exit(1)

        for key in data.keys():
            # Invalid key in json file
            if key not in valid_keys:
                LOG.error('Unexpected JSON key "%s". This value is currently '
                          'not supported.' % key)
                sys.exit(1)


# The command option will be built up and written to '/command_options'.
# which will be added to the end of $CMD in start.sh as $ARGS.
def write_command_options(args):
    with open('/command_options', 'w+') as f:
        f.write(args)


def copy_configurations():
    json_path = '/opt/kolla/config_files/config.json'

    LOG.info('Loading config json file "%s".' % json_path)

    # If JSON file is empty don't move any configs.
    # It's required there always be at least 'command' in the json file
    with open(json_path) as conf:
        try:
            config = json.load(conf)
        except ValueError:
            LOG.error('Empty config json file present. There are no config '
                      'files being moved.')
            sys.exit(1)

    json_key_validation(config)

    # Save the 'command' specified in the json file so start.sh can
    # consume it.
    cmd = config.get('command')
    write_command_options(cmd)

    for data in config.get('config_files'):
        dest_path = data.get('dest')
        source_path = data.get('source')
        config_owner = data.get('owner')
        LOG.info('The command being run is "%s"' % cmd)

        # Make sure all the proper config dirs are in place.
        if os.path.isdir(dest_path):
            # The destination is a dir
            LOG.info('Checking if parent directories for "%s" exist.'
                     % dest_path)
        else:
            # The destination is a file
            dest_path = os.path.dirname(data.get('dest'))
            LOG.info('Checking if parent directories for "%s" exist.'
                     % dest_path)

        if os.path.exists(dest_path):
            LOG.info('Config destination "%s" has the proper directories '
                     'in place.' % dest_path)
        else:
            os.makedirs(dest_path)
            LOG.info('Creating directory "%s" because it was not found.'
                     % dest_path)

        # Copy over the config file(s).
        if os.path.isdir(source_path):
            # The source is a dir
            LOG.info('Checking if there are any config files mounted '
                     'in "%s".' % source_path)
            config_files = os.listdir(source_path)
            if config_files == []:
                LOG.warning('The source directory "%s" is empty. No '
                            'config files will be copied.'
                            % source_path)
            else:
                # Source and dest need to either both be dirs or files
                if os.path.isdir(dest_path):
                    for config in config_files:
                        shutil.copy(config, dest_path)
                        LOG.info('Config file found. Copying config file '
                                 '"%s" to "%s".'
                                 % (config, dest_path))
                else:
                    LOG.error('If you specify the config source as a '
                              'directory, then the destination also needs '
                              'to be a directory')
                    sys.exit(1)
        else:
            # The source is a file
            LOG.info('Checking if there is a config file mounted in "%s".'
                     % (source_path))
            if os.path.exists(source_path):
                shutil.copy(source_path, dest_path)
                LOG.info('Config file found. Copying config file "%s" to '
                         '"%s".' % (source_path, dest_path))

                if dest_path in cmd:
                    LOG.info('Using config file: "%s" to start the %s '
                             'service'
                             % (source_path, config_owner))
                else:
                    LOG.warning('The config file "%s" is present, but you '
                                'are not using it when starting %s. '
                                % (source_path, config_owner))
            else:
                LOG.warning('Skipping config "%s" because it was not '
                            'mounted at the expected location: "%s".'
                            % (dest_path, source_path))

        # Check for user and group id in the environment.
        try:
            uid = getpwnam(config_owner).pw_uid
        except KeyError:
            LOG.error('The user "%s" does not exist.'
                      % config_owner)
            sys.exit(1)
        try:
            gid = getpwnam(config_owner).pw_gid
        except KeyError:
            LOG.error('The group "%s" doesn\'t exist.'
                      % config_owner)
            sys.exit(1)

        # Give config file proper perms.
        try:
            os.chown(dest_path, uid, gid)
        except OSError as e:
            LOG.error("Couldn't chown file %s because of"
                      "os error %s." % (dest_path, e))
            sys.exit(1)
        try:
            os.chmod(dest_path, int(data.get('perm')))
        except OSError as e:
            LOG.error("Couldn't chown file %s because of"
                      "os error %s." % (dest_path, e))
            sys.exit(1)


def execute_config_strategy():
    try:
        kolla_config_strategy = os.environ.get("KOLLA_CONFIG_STRATEGY")
    except KeyError:
        LOG.error("KOLLA_CONFIG_STRATEGY is not set properly.")
        sys.exit(1)

    if kolla_config_strategy == "COPY_ALWAYS":
        # Read all existing json files.
        copy_configurations()
    elif kolla_config_strategy == "COPY_ONCE":
        if os.path.exists('/configured'):
            LOG.info("This container has already been configured; "
                     "Refusing to copy new configs.")
            sys.exit(0)
        else:
            copy_configurations()
            f = open('/configured', 'w+')
            f.close()

    else:
        LOG.error("KOLLA_CONFIG_STRATEGY is not set properly: %s."
                  % kolla_config_strategy)
        sys.exit(1)


def main():
    execute_config_strategy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
