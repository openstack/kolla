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

from kolla.template import methods
from kolla.tests import base


class MethodsTest(base.TestCase):

    def test_debian_package_install(self):
        packages = ['https://packages.debian.org/package1.deb', 'package2.deb']
        result = methods.debian_package_install(packages)
        expectCmd = 'apt-get -y install --no-install-recommends package2.deb'
        self.assertEqual(expectCmd, result.split("&&")[1].strip())
