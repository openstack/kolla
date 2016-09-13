#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tests import clients
import testtools


# TODO(jeffrey4l): remove this skip when this test can passed.
@testtools.skip
class KeystoneTest(testtools.TestCase):
    def setUp(self):
        super(KeystoneTest, self).setUp()
        self.kc = clients.OpenStackClients().get_client('KeystoneClient')

    def test_tenants(self):
        result = self.kc.tenants.list()
        # only admin tenant
        self.assertEqual(1, len(result))
