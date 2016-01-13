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

import imp
import json
import mock
import os.path
import sys
import tempfile

from oslotest import base
import testscenarios
from zake import fake_client

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
            set_configs.load_config()
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
                set_configs.load_config()
                self.assertEqual([mock.call('/run_command', 'w+'),
                                  mock.call().__enter__(),
                                  mock.call().write(u'/bin/true'),
                                  mock.call().__exit__(None, None, None)],
                                 mo.mock_calls)


class ZkCopyTest(testscenarios.WithScenarios, base.BaseTestCase):

    scenarios = [
        ('1', dict(in_paths=['a.conf'],
                   in_subtree='/',
                   expect_paths=[['a.conf']])),
        ('2', dict(in_paths=['/a/b/c.x', '/a/b/foo.x', '/a/no.x'],
                   in_subtree='/a/b',
                   expect_paths=[['c.x'], ['foo.x']])),
        ('3', dict(in_paths=['/a/b/c.x', '/a/z/foo.x'],
                   in_subtree='/',
                   expect_paths=[['a', 'b', 'c.x'], ['a', 'z', 'foo.x']])),
    ]

    def setUp(self):
        super(ZkCopyTest, self).setUp()
        self.client = fake_client.FakeClient()
        self.client.start()
        self.addCleanup(self.client.stop)
        self.addCleanup(self.client.close)

    def test_cp_tree(self):
        # Note: oslotest.base cleans up all tempfiles as follows:
        # self.useFixture(fixtures.NestedTempfile())
        # so we don't have to.
        temp_dir = tempfile.mkdtemp()

        for path in self.in_paths:
            self.client.create(path, b'one', makepath=True)
        set_configs.zk_copy_tree(self.client, self.in_subtree, temp_dir)
        for expect in self.expect_paths:
            expect.insert(0, temp_dir)
            expect_path = os.path.join(*expect)
            self.assertTrue(os.path.exists(expect_path))


class ZkExistsTest(base.BaseTestCase):
    def setUp(self):
        super(ZkExistsTest, self).setUp()
        self.client = fake_client.FakeClient()
        self.client.start()
        self.addCleanup(self.client.stop)
        self.addCleanup(self.client.close)

    def test_path_exists_no(self):
        self.client.create('/test/path/thing', b'one', makepath=True)
        self.assertFalse(set_configs.zk_path_exists(self.client,
                                                    '/test/missing/thing'))

    def test_path_exists_yes(self):
        self.client.create('/test/path/thing', b'one', makepath=True)
        self.assertTrue(set_configs.zk_path_exists(self.client,
                                                   '/test/path/thing'))
