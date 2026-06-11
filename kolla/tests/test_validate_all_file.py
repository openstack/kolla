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

import importlib.util
import os
import tempfile
from unittest import mock

from kolla.tests import base

_VALIDATE_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'tools',
                 'validate-all-file.py'))
_spec = importlib.util.spec_from_file_location('validate_all_file',
                                               _VALIDATE_SCRIPT)
validate_all_file = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_all_file)

_SSTI_PAYLOAD = (
    "{{ self.__init__.__globals__['__builtins__']"
    "['__import__']('os').popen('id').read() }}"
)


class ValidateAllFileTest(base.TestCase):

    def test_check_json_j2_ssti_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            malicious = os.path.join(tmpdir, 'test.json.j2')
            with open(malicious, 'w') as f:
                f.write(_SSTI_PAYLOAD + '\n')
            with mock.patch.object(validate_all_file, 'PROJECT_ROOT', tmpdir):
                result = validate_all_file.check_json_j2()
        self.assertEqual(1, result)
