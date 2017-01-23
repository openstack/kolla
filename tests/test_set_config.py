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

import collections
import copy
import imp
import json
import mock
import os.path
import sys

from oslotest import base

# nasty: to import set_config (not a part of the kolla package)
this_dir = os.path.dirname(sys.modules[__name__].__file__)
set_configs_file = os.path.abspath(
    os.path.join(this_dir, '..',
                 'docker', 'base', 'set_configs.py'))

set_configs = imp.load_source('set_configs', set_configs_file)


class LoadFromFile(base.BaseTestCase):

    def test_load_ok(self):
        in_config = json.dumps({'command': '/bin/true',
                                'config_files': {}})

        mo = mock.mock_open(read_data=in_config)
        with mock.patch.object(set_configs, 'open', mo):
            config = set_configs.load_config()
            set_configs.copy_config(config)
            self.assertEqual([
                mock.call('/var/lib/kolla/config_files/config.json'),
                mock.call().__enter__(),
                mock.call().read(),
                mock.call().__exit__(None, None, None),
                mock.call('/run_command', 'w+'),
                mock.call().__enter__(),
                mock.call().write(u'/bin/true'),
                mock.call().__exit__(None, None, None)], mo.mock_calls)


class LoadFromEnv(base.BaseTestCase):

    def test_load_ok(self):
        in_config = json.dumps({'command': '/bin/true',
                                'config_files': {}})

        mo = mock.mock_open()
        with mock.patch.object(set_configs, 'open', mo):
            with mock.patch.dict('os.environ', {'KOLLA_CONFIG': in_config}):
                config = set_configs.load_config()
                set_configs.copy_config(config)
                self.assertEqual([mock.call('/run_command', 'w+'),
                                  mock.call().__enter__(),
                                  mock.call().write(u'/bin/true'),
                                  mock.call().__exit__(None, None, None)],
                                 mo.mock_calls)

FAKE_CONFIG_FILES = [
    set_configs.ConfigFile(
        '/var/lib/kolla/config_files/bar.conf',
        '/foo/bar.conf', 'user1', '0644')
]

FAKE_CONFIG_FILE = FAKE_CONFIG_FILES[0]


class ConfigFileTest(base.BaseTestCase):

    @mock.patch('os.path.exists', return_value=False)
    def test_delete_path_not_exists(self, mock_exists):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._delete_path(config_file.dest)

        mock_exists.assert_called_with(config_file.dest)

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('shutil.rmtree')
    def test_delete_path_exist_dir(self,
                                   mock_rmtree,
                                   mock_isdir,
                                   mock_exists):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._delete_path(config_file.dest)

        mock_exists.assert_called_with(config_file.dest)
        mock_isdir.assert_called_with(config_file.dest)
        mock_rmtree.assert_called_with(config_file.dest)

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('os.remove')
    def test_delete_path_exist_file(self,
                                    mock_remove,
                                    mock_isdir,
                                    mock_exists):

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._delete_path(config_file.dest)

        mock_exists.assert_called_with(config_file.dest)
        mock_isdir.assert_called_with(config_file.dest)
        mock_remove.assert_called_with(config_file.dest)

    @mock.patch('os.chmod')
    @mock.patch('os.chown')
    @mock.patch('pwd.getpwnam')
    def test_set_permission(self,
                            mock_getpwnam,
                            mock_chown,
                            mock_chmod):

        User = collections.namedtuple('User', ['pw_uid', 'pw_gid'])
        user = User(3333, 4444)
        mock_getpwnam.return_value = user

        config_file = copy.deepcopy(FAKE_CONFIG_FILE)
        config_file._set_permission(config_file.dest)

        mock_getpwnam.assert_called_with(config_file.owner)
        mock_chown.assert_called_with(config_file.dest, 3333, 4444)
        mock_chmod.assert_called_with(config_file.dest, 420)

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

    @mock.patch.object(set_configs.ConfigFile, '_copy_dir')
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch.object(set_configs.ConfigFile, '_create_parent_dirs')
    @mock.patch.object(set_configs.ConfigFile, '_delete_path')
    @mock.patch('glob.glob')
    def test_copy_one_source_dir(self, mock_glob, mock_delete_path,
                                 mock_create_parent_dirs, mock_isdir,
                                 mock_copy_dir):
        config_file = copy.deepcopy(FAKE_CONFIG_FILE)

        mock_glob.return_value = [config_file.source]

        config_file.copy()

        mock_glob.assert_called_with(config_file.source)
        mock_delete_path.assert_called_with(config_file.dest)
        mock_create_parent_dirs.assert_called_with(config_file.dest)
        mock_isdir.assert_called_with(config_file.source)
        mock_copy_dir.assert_called_with(config_file.source,
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
