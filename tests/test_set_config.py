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

import copy
import importlib.util
import json
import os.path
import sys
from unittest import mock

from oslotest import base


def load_module(name, path):
    module_spec = importlib.util.spec_from_file_location(
        name, path
    )
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


# nasty: to import set_config (not a part of the kolla package)
this_dir = os.path.dirname(sys.modules[__name__].__file__)
set_configs_file = os.path.abspath(
    os.path.join(this_dir, '..',
                 'docker', 'base', 'set_configs.py'))

set_configs = load_module('set_configs', set_configs_file)


class LoadFromFile(base.BaseTestCase):

    def test_load_ok(self):
        in_config = json.dumps({'command': '/bin/true',
                                'config_files': {}})

        mo = mock.mock_open(read_data=in_config)
        with mock.patch.object(set_configs, 'open', mo):
            config = set_configs.load_config()
            set_configs.copy_config(config)
            if sys.version_info >= (3, 13):
                calls = [
                 mock.call('/var/lib/kolla/config_files/config.json'),
                 mock.call().__enter__(),
                 mock.call().read(),
                 mock.call().__exit__(None, None, None),
                 mock.call().close(),
                 mock.call('/run_command', 'w+'),
                 mock.call().__enter__(),
                 mock.call().write('/bin/true'),
                 mock.call().__exit__(None, None, None),
                 mock.call().close()
                ]
            else:
                calls = [
                 mock.call('/var/lib/kolla/config_files/config.json'),
                 mock.call().__enter__(),
                 mock.call().read(),
                 mock.call().__exit__(None, None, None),
                 mock.call('/run_command', 'w+'),
                 mock.call().__enter__(),
                 mock.call().write('/bin/true'),
                 mock.call().__exit__(None, None, None)
                ]

            self.assertEqual(calls, mo.mock_calls)


FAKE_CONFIG_FILES = [
    set_configs.ConfigFile(
        '/var/lib/kolla/config_files/bar.conf',
        '/foo/bar.conf', 'user1', '0644')
]

FAKE_CONFIG_FILE = FAKE_CONFIG_FILES[0]


class ConfigFileTest(base.BaseTestCase):

    @mock.patch('os.path.lexists', return_value=False)
    def test_delete_path_not_exists(self, mock_lexists):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._delete_path(config_file.dest)

        mock_lexists.assert_called_with(config_file.dest)

    @mock.patch('os.path.lexists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('shutil.rmtree')
    def test_delete_path_exist_dir(self,
                                   mock_rmtree,
                                   mock_isdir,
                                   mock_lexists):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._delete_path(config_file.dest)

        mock_lexists.assert_called_with(config_file.dest)
        mock_isdir.assert_called_with(config_file.dest)
        mock_rmtree.assert_called_with(config_file.dest)

    @mock.patch('os.path.lexists', return_value=True)
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('os.remove')
    def test_delete_path_exist_file(self,
                                    mock_remove,
                                    mock_isdir,
                                    mock_lexists):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._delete_path(config_file.dest)

        mock_lexists.assert_called_with(config_file.dest)
        mock_isdir.assert_called_with(config_file.dest)
        mock_remove.assert_called_with(config_file.dest)

    @mock.patch('shutil.copystat')
    @mock.patch('os.stat')
    @mock.patch('os.chown')
    def test_set_properties_from_file(self,
                                      mock_chown,
                                      mock_stat,
                                      mock_copystat):

        stat_result = mock.MagicMock()
        mock_stat.return_value = stat_result

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._set_properties_from_file(config_file.source,
                                              config_file.dest)

        mock_copystat.assert_called_with(config_file.source, config_file.dest)
        mock_stat.assert_called_with(config_file.source)
        mock_chown.assert_called_with(config_file.dest, stat_result.st_uid,
                                      stat_result.st_gid)

    @mock.patch('os.chmod')
    @mock.patch.object(set_configs, 'handle_permissions')
    def test_set_properties_from_conf(self,
                                      mock_handle_permissions,
                                      mock_chmod):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._set_properties_from_conf(config_file.dest)
        mock_handle_permissions.assert_called_with({'permissions':
                                                    [{'owner': 'user1',
                                                      'path': config_file.dest,
                                                      'perm': '0644'}]})

    @mock.patch('glob.glob', return_value=[])
    def test_copy_no_source_not_optional(self,
                                         mock_glob):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)

        self.assertRaises(set_configs.MissingRequiredSource,
                          config_file.copy)

    @mock.patch('glob.glob', return_value=[])
    def test_copy_no_source_optional(self, mock_glob):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file.optional = True

        config_file.copy()

        mock_glob.assert_called_with(config_file.source)

    @mock.patch.object(set_configs.ConfigFile, '_copy_file')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch.object(set_configs.ConfigFile, '_create_parent_dirs')
    @mock.patch.object(set_configs.ConfigFile, '_delete_path')
    @mock.patch('glob.glob')
    def test_copy_one_source_file(self, mock_glob, mock_delete_path,
                                  mock_create_parent_dirs, mock_isdir,
                                  mock_copy_file):
        config_file = copy.deepcopy(FAKE_CONFIG_FILE)

        mock_glob.return_value = [config_file.source]

        config_file.copy()

        mock_glob.assert_called_with(config_file.source)
        mock_delete_path.assert_called_with(config_file.dest)
        mock_create_parent_dirs.assert_called_with(config_file.dest)
        mock_isdir.assert_called_with(config_file.source)
        mock_copy_file.assert_called_with(config_file.source,
                                          config_file.dest)

    @mock.patch.object(set_configs.ConfigFile, '_merge_directories')
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch.object(set_configs.ConfigFile, '_create_parent_dirs')
    @mock.patch.object(set_configs.ConfigFile, '_delete_path')
    @mock.patch('glob.glob')
    def test_copy_one_source_dir(self, mock_glob, mock_delete_path,
                                 mock_create_parent_dirs, mock_isdir,
                                 mock_merge_directories):
        config_file = copy.deepcopy(FAKE_CONFIG_FILE)

        mock_glob.return_value = [config_file.source]

        config_file.copy()

        mock_glob.assert_called_with(config_file.source)
        mock_delete_path.assert_called_with(config_file.dest)
        mock_create_parent_dirs.assert_called_with(config_file.dest)
        mock_merge_directories.assert_called_with(config_file.source,
                                                  config_file.dest)

    @mock.patch.object(set_configs.ConfigFile, '_copy_file')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch.object(set_configs.ConfigFile, '_create_parent_dirs')
    @mock.patch.object(set_configs.ConfigFile, '_delete_path')
    @mock.patch('glob.glob')
    def test_copy_glob_source_file(self, mock_glob, mock_delete_path,
                                   mock_create_parent_dirs, mock_isdir,
                                   mock_copy_file):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar.*', '/foo/', 'user1', '0644')

        mock_glob.return_value = ['/var/lib/kolla/config_files/bar.conf',
                                  '/var/lib/kolla/config_files/bar.yml']

        config_file.copy()

        mock_glob.assert_called_with(config_file.source)

        self.assertEqual(mock_delete_path.mock_calls,
                         [mock.call('/foo/bar.conf'),
                          mock.call('/foo/bar.yml')])
        self.assertEqual(mock_create_parent_dirs.mock_calls,
                         [mock.call('/foo/bar.conf'),
                          mock.call('/foo/bar.yml')])
        self.assertEqual(mock_isdir.mock_calls,
                         [mock.call('/var/lib/kolla/config_files/bar.conf'),
                          mock.call('/var/lib/kolla/config_files/bar.yml')])
        self.assertEqual(mock_copy_file.mock_calls,
                         [mock.call('/var/lib/kolla/config_files/bar.conf',
                                    '/foo/bar.conf'),
                          mock.call('/var/lib/kolla/config_files/bar.yml',
                                    '/foo/bar.yml')])

    @mock.patch.object(set_configs.ConfigFile, '_cmp_file')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('glob.glob')
    def test_check_glob_source_file(self, mock_glob, mock_isdir,
                                    mock_cmp_file):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar.*', '/foo/', 'user1', '0644')

        mock_glob.return_value = ['/var/lib/kolla/config_files/bar.conf',
                                  '/var/lib/kolla/config_files/bar.yml']
        mock_cmp_file.return_value = True

        config_file.check()

        self.assertEqual(mock_isdir.mock_calls,
                         [mock.call('/var/lib/kolla/config_files/bar.conf'),
                          mock.call('/var/lib/kolla/config_files/bar.yml')])
        self.assertEqual(mock_cmp_file.mock_calls,
                         [mock.call('/var/lib/kolla/config_files/bar.conf',
                                    '/foo/bar.conf'),
                          mock.call('/var/lib/kolla/config_files/bar.yml',
                                    '/foo/bar.yml')])

    @mock.patch.object(set_configs.ConfigFile, '_cmp_file')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('glob.glob')
    def test_check_glob_source_file_no_equal(self, mock_glob, mock_isdir,
                                             mock_cmp_file):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar.*', '/foo/', 'user1', '0644')

        mock_glob.return_value = ['/var/lib/kolla/config_files/bar.conf',
                                  '/var/lib/kolla/config_files/bar.yml']
        mock_cmp_file.side_effect = [True, False]

        self.assertRaises(set_configs.ConfigFileBadState,
                          config_file.check)

        self.assertEqual(mock_isdir.mock_calls,
                         [mock.call('/var/lib/kolla/config_files/bar.conf'),
                          mock.call('/var/lib/kolla/config_files/bar.yml')])
        self.assertEqual(mock_cmp_file.mock_calls,
                         [mock.call('/var/lib/kolla/config_files/bar.conf',
                                    '/foo/bar.conf'),
                          mock.call('/var/lib/kolla/config_files/bar.yml',
                                    '/foo/bar.yml')])

    @mock.patch.object(set_configs.ConfigFile, '_cmp_file')
    @mock.patch.object(set_configs.ConfigFile, '_cmp_dir')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('glob.glob')
    def test_check_source_dir(self, mock_glob, mock_isdir, mock_cmp_dir,
                              mock_cmp_file):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644')

        mock_glob.return_value = ['/var/lib/kolla/config_files/bar']
        mock_isdir.return_value = True
        mock_cmp_dir.return_value = True

        config_file.check()

        mock_isdir.assert_called_once_with('/var/lib/kolla/config_files/bar')
        mock_cmp_dir.assert_called_once_with(
            '/var/lib/kolla/config_files/bar', '/foo')
        mock_cmp_file.assert_not_called()

    @mock.patch.object(set_configs.ConfigFile, '_cmp_file')
    @mock.patch.object(set_configs.ConfigFile, '_cmp_dir')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('glob.glob')
    def test_check_source_dir_no_equal(self, mock_glob, mock_isdir,
                                       mock_cmp_dir, mock_cmp_file):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644')

        mock_glob.return_value = ['/var/lib/kolla/config_files/bar']
        mock_isdir.return_value = True
        mock_cmp_dir.return_value = False

        self.assertRaises(set_configs.ConfigFileBadState,
                          config_file.check)

        mock_isdir.assert_called_once_with('/var/lib/kolla/config_files/bar')
        mock_cmp_dir.assert_called_once_with(
            '/var/lib/kolla/config_files/bar', '/foo')
        mock_cmp_file.assert_not_called()

    @mock.patch('grp.getgrgid', autospec=True)
    @mock.patch('pwd.getpwuid', autospec=True)
    @mock.patch('os.stat', autospec=True)
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('os.path.exists', autospec=True)
    def test_cmp_file_opens_both_files_rb(self, mock_os_exists, mock_open,
                                          mock_os_stat, mock_pwd_getpwuid,
                                          mock_grp_getgrgid):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644')

        mock_os_exists.return_value = True
        mock_os_stat.return_value.st_mode = int('0o100644', 8)
        mock_pwd_getpwuid.return_value.pw_name = 'user1'
        mock_grp_getgrgid.return_value.gr_name = 'user1'

        self.assertIs(True,
                      config_file._cmp_file('/fake/file1', '/fake/file2'))

        self.assertEqual([mock.call('/fake/file1', 'rb'),
                          mock.call('/fake/file2', 'rb')],
                         mock_open.call_args_list)

    @mock.patch('glob.glob')
    def test_check_non_optional_src_file_not_exists(self,
                                                    mock_glob):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644')

        mock_glob.return_value = []

        self.assertRaises(set_configs.MissingRequiredSource,
                          config_file.check)

    @mock.patch('glob.glob')
    def test_check_optional_src_file_not_exists(self,
                                                mock_glob):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644',
            optional=True)
        mock_glob.return_value = []

        self.assertIsNone(config_file.check())

    @mock.patch('glob.glob')
    @mock.patch('os.path.isdir')
    @mock.patch.object(set_configs.ConfigFile, '_cmp_file')
    def test_check_raises_config_bad_state(self,
                                           mock_cmp_file,
                                           mock_isdir,
                                           mock_glob):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644',
            optional=True)
        mock_cmp_file.return_value = False
        mock_isdir.return_value = False
        mock_glob.return_value = ['/var/lib/kolla/config_files/bar']

        self.assertRaises(set_configs.ConfigFileBadState, config_file.check)

    @mock.patch('os.path.exists', autospec=True)
    def test_cmp_file_optional_src_exists_dest_no_exists(self, mock_os_exists):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644',
            optional=True)

        def fake_exists(path):
            if path == '/var/lib/kolla/config_files/bar':
                return True
            return False

        mock_os_exists.side_effect = fake_exists

        self.assertIs(False,
                      config_file._cmp_file('/var/lib/kolla/config_files/bar',
                                            '/foo'))

    @mock.patch('os.path.exists', autospec=True)
    def test_cmp_file_optional_src_no_exists_dest_exists(self, mock_os_exists):
        config_file = set_configs.ConfigFile(
            '/var/lib/kolla/config_files/bar', '/foo', 'user1', '0644',
            optional=True)

        def fake_exists(path):
            if path == '/var/lib/kolla/config_files/bar':
                return False
            return True

        mock_os_exists.side_effect = fake_exists

        self.assertIs(False,
                      config_file._cmp_file('/var/lib/kolla/config_files/bar',
                                            '/foo'))

    @mock.patch('os.makedirs')
    @mock.patch('os.path.exists')
    @mock.patch('builtins.open', new_callable=mock.mock_open,
                read_data='{"foo": "bar"}')
    def test_get_defaults_state_exist(
            self, mock_open, mock_exists, mock_makedirs):
        """Test get_defaults_state() when the default state file exists.

        This test mocks the behavior of the function when the default state
        file exists. It ensures that:
        - The directory for Kolla defaults is created if needed.
        - The state file is opened and read successfully.
        - The correct state data is returned as a dictionary.

        Mocks:
        - os.makedirs: Ensures the directory is created.
        - os.path.exists: Simulates that the state file exists.
        - open: Mocks the file opening and reading, returning a sample JSON
                content.
        """

        # Simulate that the state file exists
        mock_exists.side_effect = lambda \
            path: path == set_configs.KOLLA_DEFAULTS_STATE

        result = set_configs.get_defaults_state()

        # Check that the directory creation was called
        mock_makedirs.assert_called_once_with(set_configs.KOLLA_DEFAULTS,
                                              exist_ok=True)

        # Verify that the function checked if the state file exists
        mock_exists.assert_called_once_with(set_configs.KOLLA_DEFAULTS_STATE)

        # Verify that the state file was opened for reading
        mock_open.assert_called_once_with(
            set_configs.KOLLA_DEFAULTS_STATE, 'r')

        # Validate the result is as expected
        self.assertEqual(result, {"foo": "bar"})

    @mock.patch('os.makedirs')
    @mock.patch('os.path.exists', return_value=False)
    def test_get_defaults_state_not_exist(self, mock_exists, mock_makedirs):
        """Test get_defaults_state() when the default state file doesn't exist.

        This test simulates the scenario where the default state file is
        missing.
        It verifies that:
        - The directory for Kolla defaults is created if needed.
        - The state file is checked but not found.
        - An empty dictionary is returned since the state file is missing.

        Mocks:
        - os.makedirs: Ensures the directory is created.
        - os.path.exists: Simulates that the state file does not exist.
        """

        # Simulate that the file does not exist
        mock_exists.side_effect = lambda path: False

        result = set_configs.get_defaults_state()

        # Check that the directory creation was called
        mock_makedirs.assert_called_once_with(set_configs.KOLLA_DEFAULTS,
                                              exist_ok=True)
        # Verify that the function checked if the state file exists
        mock_exists.assert_called_once_with(set_configs.KOLLA_DEFAULTS_STATE)

        # Result should be an empty dictionary since the state file is missing
        self.assertEqual(result, {})

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('json.dump')
    def test_set_defaults_state(self, mock_json_dump, mock_open):
        """Test set_defaults_state() to ensure proper saving of the state.

        This test verifies that the provided state is correctly saved as a JSON
        file with proper indentation. It checks:
        - The state file is opened for writing.
        - The provided state dictionary is dumped into the file in JSON format
          with indentation for readability.

        Mocks:
        - open: Mocks the file opening for writing.
        - json.dump: Mocks the JSON dumping process.
        """

        state = {"foo": "bar"}

        set_configs.set_defaults_state(state)

        # Ensure the state file is opened for writing
        mock_open.assert_called_once_with(
            set_configs.KOLLA_DEFAULTS_STATE, 'w')

        # Check that the JSON state is dumped with proper indentation
        mock_json_dump.assert_called_once_with(state, mock_open(), indent=4)

    @mock.patch.object(set_configs, 'set_defaults_state')
    @mock.patch.object(set_configs, 'ConfigFile')
    @mock.patch('os.path.exists')
    @mock.patch.object(set_configs, 'get_defaults_state', return_value={})
    def test_handle_defaults_state_not_exist_config_exist(
            self, mock_get_defaults_state, mock_exists, mock_config_file,
            mock_set_defaults_state):
        """Test handle_defaults() when no existing default config is present.

        This test simulates the case where no prior default configuration file
        exists and a new configuration file needs to be backed up. It verifies:
        - The current default state is retrieved (empty in this case).
        - The configuration file exists, and a backup is created for it.
        - The new state is saved after processing the configuration.

        Mocks:
        - get_defaults_state: Returns an empty state.
        - os.path.exists: Simulates that the source file exists.
        - ConfigFile: Mocks the behavior of the ConfigFile class for file
          copying.
        - set_defaults_state: Ensures the new state is saved.
        """

        config = {
            'config_files': [
                {
                    'source': '/source/file', 'dest': '/dest/file'
                 }
            ]
        }

        # Simulate the file exists
        mock_exists.return_value = True

        copy = {
            'source': '/dest/file',
            'dest': set_configs.KOLLA_DEFAULTS + '/dest/file',
            'preserve_properties': True
        }

        expected_state = {
            '/dest/file': copy
        }

        # Create a mock instance of ConfigFile
        mock_config_file_instance = mock_config_file.return_value
        mock_config_file_instance.copy = mock.MagicMock()

        # Call the function being tested
        set_configs.handle_defaults(config)

        # Check that the directory creation was called
        mock_get_defaults_state.assert_called_once()

        # Verify that the ConfigFile was instantiated correctly
        mock_config_file.assert_called_once_with(**copy)

        # Ensure the copy method was called for the ConfigFile instance
        mock_config_file_instance.copy.assert_called_once()

        # Check that the updated state was saved
        mock_set_defaults_state.assert_called_once_with(expected_state)

    @mock.patch.object(set_configs, 'set_defaults_state')
    @mock.patch.object(set_configs, 'ConfigFile')
    @mock.patch('os.path.exists')
    @mock.patch.object(set_configs, 'get_defaults_state', return_value={})
    def test_handle_defaults_state_not_exist_config_not_exist(
            self, mock_get_defaults_state, mock_exists, mock_config_file,
            mock_set_defaults_state):
        """Test handle_defaults() with no config file and no default state.

        This test simulates the scenario where the configuration file does not
        exist, and no existing default state is present. It verifies:
        - The current default state is retrieved (empty).
        - Since the configuration file doesn't exist, no backup is made.
        - The state is updated accordingly.

        Mocks:
        - get_defaults_state: Returns an empty state.
        - os.path.exists: Simulates that the source
                          exists (in /var/lib/kolla/config/) but the
                          destination does not
                          (real destination where file should be copied to).
        - ConfigFile: Ensures no ConfigFile instance is created since no backup
                      is needed.
        - set_defaults_state: Ensures the updated state is saved.
        """

        config = {
            'config_files': [
                {
                    'source': '/source/file', 'dest': '/dest/file'
                 }
            ]
        }

        # Simulate source exists but dest does not
        def mock_exists_side_effect(path):
            if path == '/source/file':
                return True  # Source exists
            return False  # Destination does not exist

        mock_exists.side_effect = mock_exists_side_effect

        copy = {
            'source': '/dest/file',
            'dest': None,
            'preserve_properties': True
        }

        expected_state = {
            '/dest/file': copy
        }

        # Create a mock instance of ConfigFile
        mock_config_file_instance = mock_config_file.return_value
        mock_config_file_instance.copy = mock.MagicMock()

        # Call the function being tested
        set_configs.handle_defaults(config)

        # Ensure the current default state was retrieved
        mock_get_defaults_state.assert_called_once()

        # Verify that ConfigFile was not instantiated (because
        # dest doesn't exist - nothing to backup)
        mock_config_file.assert_not_called()

        # Check that the updated state was saved
        mock_set_defaults_state.assert_called_once_with(expected_state)

    @mock.patch.object(set_configs, 'set_defaults_state')
    @mock.patch.object(set_configs, 'ConfigFile')
    @mock.patch('os.remove')
    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.isfile')
    @mock.patch('os.path.exists')
    @mock.patch.object(set_configs, 'get_defaults_state', return_value={
        "/dest/file": {
            "source": "/dest/file",
            "preserve_properties": True,
            "dest": None
        }
    })
    def test_handle_defaults_state_exist_config_exist_is_file(
            self, mock_get_defaults_state, mock_exists, mock_isfile,
            mock_rmtree, mock_remove, mock_config_file,
            mock_set_defaults_state):
        """Test handle_defaults() when the configuration exists and is a file.

        This test simulates the scenario where a configuration file already
        exists.
        It verifies:
        - The current default state is retrieved.
        - The destination is identified as a file.
        - The file is removed.
        - The updated state is saved correctly after the file is handled.

        Mocks:
        - get_defaults_state: Returns an existing state.
        - os.path.exists: Simulates the destination file exists.
        - os.path.isfile: Ensures the destination is identified as a file.
        - os.remove: Ensures the file is removed.
        - set_defaults_state: Ensures the state is saved after processing.
        """

        config = {
            'config_files': [
                {
                    'source': '/source/file', 'dest': '/dest/file'
                 }
            ]
        }

        # Simulate that destination exists and is a file
        mock_exists.side_effect = lambda path: path == "/dest/file"
        mock_isfile.side_effect = lambda path: path == "/dest/file"

        # Expected state after handling defaults
        expected_state = {
            "/dest/file": {
                "source": "/dest/file",
                "preserve_properties": True,
                "dest": None
            }
        }

        # Call the function being tested
        set_configs.handle_defaults(config)

        # Ensure the current default state was retrieved
        mock_get_defaults_state.assert_called_once()

        # Verify that the file check was performed
        mock_isfile.assert_called_once_with("/dest/file")

        # Ensure the file is removed since it exists
        mock_remove.assert_called_once_with("/dest/file")

        # Ensure rmtree was not called since it's a file, not a directory
        mock_rmtree.assert_not_called()

        # Verify that the updated state was saved
        mock_set_defaults_state.assert_called_once_with(expected_state)

    @mock.patch.object(set_configs, 'set_defaults_state')
    @mock.patch.object(set_configs, 'ConfigFile')
    @mock.patch('os.remove')
    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.isfile')
    @mock.patch('os.path.exists')
    @mock.patch.object(set_configs, 'get_defaults_state', return_value={
        "/dest/file": {
            "source": "/dest/file",
            "preserve_properties": True,
            "dest": None
        }
    })
    def test_handle_defaults_state_exist_config_exist_is_dir(
            self, mock_get_defaults_state, mock_exists, mock_isfile,
            mock_rmtree, mock_remove, mock_config_file,
            mock_set_defaults_state):
        """Test handle_defaults() when the conf file exists and is a directory.

        This test simulates the scenario where the configuration exists as
        a directory.
        It verifies:
        - The current default state is retrieved.
        - The configuration is identified as a directory.
        - The configuration directory is removed using shutil.rmtree().
        - The updated state is saved correctly after handling the directory.

        Mocks:
        - get_defaults_state: Returns an existing state.
        - os.path.exists: Simulates the destination directory exists.
        - os.path.isfile: Ensures the destination is not a file
          (it’s a directory).
        - shutil.rmtree: Ensures the directory is removed.
        - ConfigFile: Mocks the ConfigFile handling.
        - set_defaults_state: Ensures the state is saved after processing.
        """

        config = {
            'config_files': [
                {
                    'source': '/source/file', 'dest': '/dest/file'
                 }
            ]
        }

        # Simulate that destination exists and is a file
        mock_exists.side_effect = lambda path: path == "/dest/file"
        # Simulate that destination exists, but it's a directory, not a file
        mock_isfile.side_effect = lambda path: False

        # Expected state after handling defaults
        expected_state = {
            "/dest/file": {
                "source": "/dest/file",
                "preserve_properties": True,
                "dest": None
            }
        }

        # Create a mock instance of ConfigFile
        mock_config_file_instance = mock_config_file.return_value
        mock_config_file_instance.copy = mock.MagicMock()

        # Call the function being tested
        set_configs.handle_defaults(config)

        # Ensure the current default state was retrieved
        mock_get_defaults_state.assert_called_once()

        # Verify that a file check was performed
        mock_isfile.assert_called_once_with("/dest/file")

        # Check that os.remove was called for the existing file
        mock_remove.assert_not_called()

        # Since it's a directory, ensure rmtree was called to remove it
        mock_rmtree.assert_called_once_with("/dest/file")

        # Verify that the updated state was saved
        mock_set_defaults_state.assert_called_once_with(expected_state)

    @mock.patch.object(set_configs, 'set_defaults_state')
    @mock.patch.object(set_configs, 'ConfigFile')
    @mock.patch('os.path.exists')
    @mock.patch.object(set_configs, 'get_defaults_state', return_value={
        "/dest/file": {
            "source": "/source/file",
            "dest": "/dest/file",
            "preserve_properties": True
        }
    })
    def test_handle_defaults_state_exist_config_restored(
            self, mock_get_defaults_state, mock_exists, mock_config_file,
            mock_set_defaults_state):
        """Test handle_defaults() when dest is not None in the default state.

        This test simulates the case where the destination in the default state
        is not None, meaning a swap of source and destination is required.
        It verifies:
        - The current default state is retrieved.
        - The source and destination are swapped in the ConfigFile
          and restored.
        - The state is updated correctly after processing.

        Mocks:
        - get_defaults_state: Returns the current state.
        - ConfigFile: Mocks the behavior of ConfigFile with swapped
          source/dest.
        - set_defaults_state: Ensures the state is saved after the swap and
          processing.
        """

        # Configuration input (irrelevant in this case, as we're
        # only focusing on state)
        # Everything else is covered by other tests
        config = {}

        copy = {
            "source": "/dest/file",
            "dest": "/source/file",  # Swapped source and dest
            "preserve_properties": True
        }

        # Expected state after swapping source and dest
        expected_state = {
            "/dest/file": {
                "source": "/dest/file",
                "dest": "/source/file",  # Swapped source and dest
                "preserve_properties": True
            }
        }

        # Create a mock instance of ConfigFile
        mock_config_file_instance = mock_config_file.return_value
        mock_config_file_instance.copy = mock.MagicMock()

        # Call the function being tested
        set_configs.handle_defaults(config)

        # Ensure the current default state was retrieved
        mock_get_defaults_state.assert_called_once()

        # Verify that ConfigFile was instantiated with the swapped
        # source and dest
        mock_config_file.assert_called_once_with(**copy)

        # Ensure the copy method was called for the ConfigFile instance
        mock_config_file_instance.copy.assert_called_once()

        # Ensure the copy method was called on the ConfigFile instance
        mock_config_file_instance.copy.assert_called_once()

        # Verify that the updated state was saved
        mock_set_defaults_state.assert_called_once_with(expected_state)
