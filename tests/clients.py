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


from keystoneclient.v2_0 import client as ksclient
import logging

logging.basicConfig(level=logging.WARNING)
LOG = logging.getLogger(__name__)


class OpenStackClients(object):

    def __init__(self):
        self._connected_clients = {}
        self._supported_clients = self.__class__.__subclasses__()
        self.client = None

    def get_client(self, name):
        if name in self._connected_clients:
            return self._connected_clients[name]
        try:
            aclass = next(s for s in self._supported_clients if name in
                          s.__name__)
            sclient = aclass()
            connected_client = sclient.create()
            self._connected_clients[name] = connected_client
            return connected_client

        except StopIteration:
            LOG.warning("Requested client %s not found", name)
            raise

    def create(self):
        pass


class KeystoneClient(OpenStackClients):

    def __init__(self):
        super(KeystoneClient, self).__init__()
        # TODO(Jeff Peeler): this shouldn't be hard coded
        self.creds = {'auth_url': 'http://10.0.0.4:5000/v2.0',
                      'username': 'admin',
                      'password': 'steakfordinner',
                      'tenant_name': 'admin'}

    def create(self):
        if self.client is None:
            self.client = ksclient.Client(**self.creds)
        return self.client


if __name__ == '__main__':
    # TODO(Jeff Peeler): mox this
    client_mgr = OpenStackClients()
    ks = client_mgr.get_client('KeystoneClient')
    LOG.info(ks)
    ks2 = client_mgr.get_client('KeystoneClient')
    LOG.info(ks2)
