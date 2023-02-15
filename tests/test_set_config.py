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
            self.assertEqual([
                mock.call('/var/lib/kolla/config_files/config.json'),
                mock.call().__enter__(),
                mock.call().read(),
                mock.call().__exit__(None, None, None),
                mock.call('/run_command', 'w+'),
                mock.call().__enter__(),
                mock.call().write('/bin/true'),
                mock.call().__exit__(None, None, None)], mo.mock_calls)


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
