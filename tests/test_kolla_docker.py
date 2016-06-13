#!/usr/bin/python

# Copyright 2016 NEC Corporation
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
import os
import sys

try:
    from unittest import mock
except ImportError:
    import mock
from oslotest import base

this_dir = os.path.dirname(sys.modules[__name__].__file__)
sys.modules['ansible'] = mock.MagicMock()
sys.modules['ansible.module_utils'] = mock.MagicMock()
sys.modules['ansible.module_utils.basic'] = mock.MagicMock()
kolla_docker_file = os.path.join(this_dir, '..', 'ansible',
                                 'library', 'kolla_docker.py')
kd = imp.load_source('kolla_docker', kolla_docker_file)


class ModuleArgsTest(base.BaseTestCase):

    def setUp(self):
        super(ModuleArgsTest, self).setUp()

    def test_module_args(self):
        argument_spec = dict(
            common_options=dict(required=False, type='dict', default=dict()),
            action=dict(
                requried=True, type='str', choices=['compare_image',
                                                    'create_volume',
                                                    'get_container_env',
                                                    'get_container_state',
                                                    'pull_image',
                                                    'remove_container',
                                                    'remove_volume',
                                                    'restart_container',
                                                    'start_container',
                                                    'stop_container']),
            api_version=dict(required=False, type='str', default='auto'),
            auth_email=dict(required=False, type='str'),
            auth_password=dict(required=False, type='str'),
            auth_registry=dict(required=False, type='str'),
            auth_username=dict(required=False, type='str'),
            detach=dict(required=False, type='bool', default=True),
            labels=dict(required=False, type='dict', default=dict()),
            name=dict(required=False, type='str'),
            environment=dict(required=False, type='dict'),
            image=dict(required=False, type='str'),
            ipc_mode=dict(required=False, type='str', choices=['host']),
            cap_add=dict(required=False, type='list', default=list()),
            security_opt=dict(required=False, type='list', default=list()),
            pid_mode=dict(required=False, type='str', choices=['host']),
            privileged=dict(required=False, type='bool', default=False),
            remove_on_exit=dict(required=False, type='bool', default=True),
            restart_policy=dict(
                required=False, type='str', choices=['no',
                                                     'never',
                                                     'on-failure',
                                                     'always']),
            restart_retries=dict(required=False, type='int', default=10),
            tls_verify=dict(required=False, type='bool', default=False),
            tls_cert=dict(required=False, type='str'),
            tls_key=dict(required=False, type='str'),
            tls_cacert=dict(required=False, type='str'),
            volumes=dict(required=False, type='list'),
            volumes_from=dict(required=False, type='list')
            )
        required_together = [
            ['tls_cert', 'tls_key']
        ]

        kd.AnsibleModule = mock.MagicMock()
        kd.generate_module()
        kd.AnsibleModule.assert_called_with(
            argument_spec=argument_spec,
            required_together=required_together,
            bypass_checks=True
        )

FAKE_DATA = {

    'params': {
        'detach': True,
        'environment': {},
        'host_config': {
            'network_mode': 'host',
            'ipc_mode': '',
            'cap_add': None,
            'security_opt': None,
            'pid_mode': '',
            'privileged': False,
            'volumes_from': None,
            'restart_policy': 'always',
            'restart_retries': 10},
        'labels': {'build-date': '2016-06-02',
                   'kolla_version': '2.0.1',
                   'license': 'GPLv2',
                   'name': 'ubuntu Base Image',
                   'vendor': 'ubuntuOS'},
        'image': 'ubuntu',
        'name': 'test_container',
        'volumes': None,
        'tty': True

    }
}


@mock.patch("docker.Client")
def get_DockerWorker(mod_param, mock_dclient):
    module = mock.MagicMock()
    module.params = mod_param
    dw = kd.DockerWorker(module)
    return dw


class TestContainer(base.BaseTestCase):

    def setUp(self):
        super(TestContainer, self).setUp()

    def test_create_container(self):
        self.dw = get_DockerWorker(FAKE_DATA['params'])
        self.dw.dc.create_host_config = mock.MagicMock(
            return_value=FAKE_DATA['params']['host_config'])
        self.dw.create_container()
        self.assertTrue(self.dw.changed)
        self.dw.dc.create_container.assert_called_once_with(
            **FAKE_DATA['params'])
