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
