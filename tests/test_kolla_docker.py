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

import copy
import imp
import os
import sys

try:
    from unittest import mock
except ImportError:
    import mock
from docker import errors as docker_error
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
                                                     'always',
                                                     'unless-stopped']),
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
            'restart_policy': 'unless-stopped',
            'restart_retries': 10},
        'labels': {'build-date': '2016-06-02',
                   'kolla_version': '2.0.1',
                   'license': 'GPLv2',
                   'name': 'ubuntu Base Image',
                   'vendor': 'ubuntuOS'},
        'image': 'myregistrydomain.com:5000/ubuntu:16.04',
        'name': 'test_container',
        'volumes': None,
        'tty': True
    },

    'images': [
        {'Created': 1462317178,
         'Labels': {},
         'VirtualSize': 120759015,
         'ParentId': '',
         'RepoTags': ['myregistrydomain.com:5000/ubuntu:16.04'],
         'Id': 'sha256:c5f1cf30',
         'Size': 120759015},
        {'Created': 1461802380,
         'Labels': {},
         'VirtualSize': 403096303,
         'ParentId': '',
         'RepoTags': ['myregistrydomain.com:5000/centos:7.0'],
         'Id': 'sha256:336a6',
         'Size': 403096303}
    ],

    'containers': [
        {'Created': 1463578194,
         'Status': 'Up 23 hours',
         'HostConfig': {'NetworkMode': 'default'},
         'Id': 'e40d8e7187',
         'Image': 'myregistrydomain.com:5000/ubuntu:16.04',
         'ImageID': 'sha256:c5f1cf30',
         'Labels': {},
         'Names': '/my_container'}
    ],

    'container_inspect': {
        'Config': {
            'Env': ['KOLLA_BASE_DISTRO=ubuntu',
                    'KOLLA_INSTALL_TYPE=binary',
                    'KOLLA_INSTALL_METATYPE=rdo'],
            'Hostname': 'node2',
            'Volumes': {'/var/lib/kolla/config_files/': {}}},
        'Mounts': {},
        'NetworkSettings': {},
        'State': {}
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
        self.fake_data = copy.deepcopy(FAKE_DATA)

    def test_create_container(self):
        self.dw = get_DockerWorker(self.fake_data['params'])
        self.dw.dc.create_host_config = mock.MagicMock(
            return_value=self.fake_data['params']['host_config'])
        self.dw.create_container()
        self.assertTrue(self.dw.changed)
        self.dw.dc.create_container.assert_called_once_with(
            **self.fake_data['params'])

    def test_start_container_without_pull(self):
        self.fake_data['params'].update({'auth_username': 'fake_user',
                                         'auth_password': 'fake_psw',
                                         'auth_registry': 'myrepo/myapp',
                                         'auth_email': 'fake_mail@foogle.com'})
        self.dw = get_DockerWorker(self.fake_data['params'])
        self.dw.dc.images = mock.MagicMock(
            return_value=self.fake_data['images'])
        self.dw.dc.containers = mock.MagicMock(params={'all': 'True'})
        new_container = copy.deepcopy(self.fake_data['containers'])
        new_container.append({'Names': '/test_container',
                              'Status': 'Up 2 seconds'})
        self.dw.dc.containers.side_effect = [self.fake_data['containers'],
                                             new_container]
        self.dw.check_container_differs = mock.MagicMock(return_value=False)
        self.dw.create_container = mock.MagicMock()
        self.dw.start_container()
        self.assertFalse(self.dw.changed)
        self.dw.create_container.assert_called_once_with()

    def test_start_container_with_duplicate_name(self):
        self.fake_data['params'].update({'name': 'my_container',
                                         'auth_username': 'fake_user',
                                         'auth_password': 'fake_psw',
                                         'auth_registry': 'myrepo/myapp',
                                         'auth_email': 'fake_mail@foogle.com'})
        self.dw = get_DockerWorker(self.fake_data['params'])
        self.dw.dc.images = mock.MagicMock(
            return_value=self.fake_data['images'])
        self.dw.dc.containers = mock.MagicMock(params={'all': 'True'})
        updated_cont_list = copy.deepcopy(self.fake_data['containers'])
        updated_cont_list.pop(0)
        self.dw.dc.containers.side_effect = [self.fake_data['containers'],
                                             self.fake_data['containers'],
                                             updated_cont_list,
                                             self.fake_data['containers']
                                             ]
        self.dw.check_container_differs = mock.MagicMock(return_value=True)
        self.dw.dc.remove_container = mock.MagicMock()
        self.dw.create_container = mock.MagicMock()
        self.dw.start_container()
        self.assertTrue(self.dw.changed)
        self.dw.dc.remove_container.assert_called_once_with(
            container=self.fake_data['params'].get('name'),
            force=True)
        self.dw.create_container.assert_called_once_with()

    def test_start_container(self):
        self.fake_data['params'].update({'name': 'my_container',
                                         'auth_username': 'fake_user',
                                         'auth_password': 'fake_psw',
                                         'auth_registry': 'myrepo/myapp',
                                         'auth_email': 'fake_mail@foogle.com'})
        self.dw = get_DockerWorker(self.fake_data['params'])
        self.dw.dc.images = mock.MagicMock(
            return_value=self.fake_data['images'])
        self.fake_data['containers'][0].update(
            {'Status': 'Exited 2 days ago'})
        self.dw.dc.containers = mock.MagicMock(
            return_value=self.fake_data['containers'])
        self.dw.check_container_differs = mock.MagicMock(return_value=False)
        self.dw.dc.start = mock.MagicMock()
        self.dw.start_container()
        self.assertTrue(self.dw.changed)
        self.dw.dc.start.assert_called_once_with(
            container=self.fake_data['params'].get('name'))

    def test_stop_container(self):
        self.dw = get_DockerWorker({'name': 'my_container',
                                    'action': 'stop_container'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.stop_container()

        self.assertTrue(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.dc.stop.assert_called_once_with('my_container')

    def test_stop_container_not_exists(self):
        self.dw = get_DockerWorker({'name': 'fake_container',
                                    'action': 'stop_container'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.stop_container()

        self.assertFalse(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.module.fail_json.assert_called_once_with(
            msg="No such container: fake_container to stop")

    def test_restart_container(self):
        self.dw = get_DockerWorker({'name': 'my_container',
                                    'action': 'restart_container'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.fake_data['container_inspect'].update(
            self.fake_data['containers'][0])
        self.dw.dc.inspect_container.return_value = (
            self.fake_data['container_inspect'])
        self.dw.restart_container()

        self.assertTrue(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.dc.inspect_container.assert_called_once_with('my_container')
        self.dw.dc.restart.assert_called_once_with('my_container')

    def test_restart_container_not_exists(self):
        self.dw = get_DockerWorker({'name': 'fake-container',
                                    'action': 'restart_container'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.restart_container()

        self.assertFalse(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.module.fail_json.assert_called_once_with(
            msg="No such container: fake-container")

    def test_remove_container(self):
        self.dw = get_DockerWorker({'name': 'my_container',
                                    'action': 'remove_container'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.remove_container()

        self.assertTrue(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.dc.remove_container.assert_called_once_with(
            container='my_container',
            force=True
        )

    def test_get_container_env(self):
        fake_env = dict(KOLLA_BASE_DISTRO='ubuntu',
                        KOLLA_INSTALL_TYPE='binary',
                        KOLLA_INSTALL_METATYPE='rdo')
        self.dw = get_DockerWorker({'name': 'my_container',
                                    'action': 'get_container_env'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.fake_data['container_inspect'].update(
            self.fake_data['containers'][0])
        self.dw.dc.inspect_container.return_value = (
            self.fake_data['container_inspect'])
        self.dw.get_container_env()

        self.assertFalse(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.dc.inspect_container.assert_called_once_with('my_container')
        self.dw.module.exit_json.assert_called_once_with(**fake_env)

    def test_get_container_env_negative(self):
        self.dw = get_DockerWorker({'name': 'fake_container',
                                    'action': 'get_container_env'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.get_container_env()

        self.assertFalse(self.dw.changed)
        self.dw.module.fail_json.assert_called_once_with(
            msg="No such container: fake_container")

    def test_get_container_state(self):
        State = {'Dead': False,
                 'ExitCode': 0,
                 'Pid': 12475,
                 'StartedAt': u'2016-06-07T11:22:37.66876269Z',
                 'Status': u'running'}
        self.fake_data['container_inspect'].update({'State': State})
        self.dw = get_DockerWorker({'name': 'my_container',
                                    'action': 'get_container_state'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.dc.inspect_container.return_value = (
            self.fake_data['container_inspect'])
        self.dw.get_container_state()

        self.assertFalse(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.dc.inspect_container.assert_called_once_with('my_container')
        self.dw.module.exit_json.assert_called_once_with(**State)

    def test_get_container_state_negative(self):
        self.dw = get_DockerWorker({'name': 'fake_container',
                                    'action': 'get_container_state'})
        self.dw.dc.containers.return_value = self.fake_data['containers']
        self.dw.get_container_state()

        self.assertFalse(self.dw.changed)
        self.dw.dc.containers.assert_called_once_with(all=True)
        self.dw.module.fail_json.assert_called_once_with(
            msg="No such container: fake_container")


class TestImage(base.BaseTestCase):

    def setUp(self):
        super(TestImage, self).setUp()
        self.fake_data = copy.deepcopy(FAKE_DATA)

    def test_check_image(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/ubuntu:16.04'})
        self.dw.dc.images.return_value = self.fake_data['images']

        return_data = self.dw.check_image()
        self.assertFalse(self.dw.changed)
        self.dw.dc.images.assert_called_once_with()
        self.assertEqual(self.fake_data['images'][0], return_data)

    def test_check_image_before_docker_1_12(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/centos:7.0'})
        self.fake_data['images'][0]['RepoTags'] = []
        self.dw.dc.images.return_value = self.fake_data['images']

        return_data = self.dw.check_image()
        self.assertFalse(self.dw.changed)
        self.dw.dc.images.assert_called_once_with()
        self.assertEqual(self.fake_data['images'][1], return_data)

    def test_check_image_docker_1_12(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/centos:7.0'})
        self.fake_data['images'][0]['RepoTags'] = None
        self.dw.dc.images.return_value = self.fake_data['images']

        return_data = self.dw.check_image()
        self.assertFalse(self.dw.changed)
        self.dw.dc.images.assert_called_once_with()
        self.assertEqual(self.fake_data['images'][1], return_data)

    def test_compare_image(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/ubuntu:16.04'})
        self.dw.dc.images.return_value = self.fake_data['images']
        container_info = {'Image': 'sha256:c5f1cf40',
                          'Config': {'myregistrydomain.com:5000/ubuntu:16.04'}
                          }

        return_data = self.dw.compare_image(container_info)
        self.assertFalse(self.dw.changed)
        self.dw.dc.images.assert_called_once_with()
        self.assertTrue(return_data)

    def test_pull_image_new(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/ubuntu:16.04',
             'auth_username': 'fake_user',
             'auth_password': 'fake_psw',
             'auth_registry': 'myrepo/myapp',
             'auth_email': 'fake_mail@foogle.com'
             })
        self.dw.dc.pull.return_value = [
            '{"status":"Pull complete","progressDetail":{},"id":"22f7"}\r\n',
            '{"status":"Digest: sha256:47c3bdbcf99f0c1a36e4db"}\r\n',
            '{"status":"Downloaded newer image for ubuntu:16.04"}\r\n'
        ]

        self.dw.pull_image()
        self.dw.dc.pull.assert_called_once_with(
            repository='myregistrydomain.com:5000/ubuntu',
            tag='16.04',
            stream=True)
        self.assertTrue(self.dw.changed)

    def test_pull_image_exists(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/ubuntu:16.04'})
        self.dw.dc.pull.return_value = [
            '{"status":"Pull complete","progressDetail":{},"id":"22f7"}\r\n',
            '{"status":"Digest: sha256:47c3bdbf0c1a36e4db"}\r\n',
            '{"status":"mage is up to date for ubuntu:16.04"}\r\n'
        ]

        self.dw.pull_image()
        self.dw.dc.pull.assert_called_once_with(
            repository='myregistrydomain.com:5000/ubuntu',
            tag='16.04',
            stream=True)
        self.assertFalse(self.dw.changed)

    def test_pull_image_unknown_status(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/ubuntu:16.04'})
        self.dw.dc.pull.return_value = [
            '{"status": "some random message"}\r\n']

        self.dw.pull_image()
        self.dw.dc.pull.assert_called_once_with(
            repository='myregistrydomain.com:5000/ubuntu',
            tag='16.04',
            stream=True)
        self.assertFalse(self.dw.changed)
        self.dw.module.fail_json.assert_called_with(
            msg='Unknown status message: some random message',
            failed=True)

    def test_pull_image_not_exists(self):
        self.dw = get_DockerWorker(
            {'image': 'unknown:16.04'})
        self.dw.dc.pull.return_value = [
            '{"error": "image unknown not found"}\r\n']

        self.dw.pull_image()
        self.dw.dc.pull.assert_called_once_with(
            repository='unknown',
            tag='16.04',
            stream=True)
        self.assertFalse(self.dw.changed)
        self.dw.module.fail_json.assert_called_once_with(
            msg="The requested image does not exist: unknown:16.04",
            failed=True)

    def test_pull_image_error(self):
        self.dw = get_DockerWorker(
            {'image': 'myregistrydomain.com:5000/ubuntu:16.04'})
        self.dw.dc.pull.return_value = [
            '{"error": "unexpected error"}\r\n']

        self.dw.pull_image()
        self.dw.dc.pull.assert_called_once_with(
            repository='myregistrydomain.com:5000/ubuntu',
            tag='16.04',
            stream=True)
        self.assertFalse(self.dw.changed)
        self.dw.module.fail_json.assert_called_once_with(
            msg="Unknown error message: unexpected error",
            failed=True)


class TestVolume(base.BaseTestCase):

    def setUp(self):
        super(TestVolume, self).setUp()
        self.fake_data = copy.deepcopy(FAKE_DATA)
        self.volumes = {
            'Volumes':
            [{'Driver': u'local',
              'Labels': None,
              'Mountpoint': '/var/lib/docker/volumes/nova_compute/_data',
              'Name': 'nova_compute'},
             {'Driver': 'local',
              'Labels': None,
              'Mountpoint': '/var/lib/docker/volumes/mariadb/_data',
              'Name': 'mariadb'}]
        }

    def test_create_volume(self):
        self.dw = get_DockerWorker({'name': 'rabbitmq',
                                    'action': 'create_volume'})
        self.dw.dc.volumes.return_value = self.volumes

        self.dw.create_volume()
        self.dw.dc.volumes.assert_called_once_with()
        self.assertTrue(self.dw.changed)
        self.dw.dc.create_volume.assert_called_once_with(
            name='rabbitmq',
            driver='local')

    def test_create_volume_exists(self):
        self.dw = get_DockerWorker({'name': 'nova_compute',
                                    'action': 'create_volume'})
        self.dw.dc.volumes.return_value = self.volumes

        self.dw.create_volume()
        self.dw.dc.volumes.assert_called_once_with()
        self.assertFalse(self.dw.changed)

    def test_remove_volume(self):
        self.dw = get_DockerWorker({'name': 'nova_compute',
                                    'action': 'remove_volume'})
        self.dw.dc.volumes.return_value = self.volumes

        self.dw.remove_volume()
        self.assertTrue(self.dw.changed)
        self.dw.dc.remove_volume.assert_called_once_with(name='nova_compute')

    def test_remove_volume_not_exists(self):
        self.dw = get_DockerWorker({'name': 'rabbitmq',
                                    'action': 'remove_volume'})
        self.dw.dc.volumes.return_value = self.volumes

        self.dw.remove_volume()
        self.assertFalse(self.dw.changed)

    def test_remove_volume_exception(self):
        resp = mock.MagicMock()
        resp.status_code = 409
        docker_except = docker_error.APIError('test error', resp)
        self.dw = get_DockerWorker({'name': 'nova_compute',
                                    'action': 'remove_volume'})
        self.dw.dc.volumes.return_value = self.volumes
        self.dw.dc.remove_volume.side_effect = docker_except

        self.assertRaises(docker_error.APIError, self.dw.remove_volume)
        self.assertTrue(self.dw.changed)
        self.dw.module.fail_json.assert_called_once_with(
            failed=True,
            msg="Volume named 'nova_compute' is currently in-use"
        )


class TestAttrComp(base.BaseTestCase):

    def setUp(self):
        super(TestAttrComp, self).setUp()
        self.fake_data = copy.deepcopy(FAKE_DATA)

    def test_compare_cap_add_neg(self):
        container_info = {'HostConfig': dict(CapAdd=['data'])}
        self.dw = get_DockerWorker({'cap_add': ['data']})
        self.assertFalse(self.dw.compare_cap_add(container_info))

    def test_compare_cap_add_pos(self):
        container_info = {'HostConfig': dict(CapAdd=['data1'])}
        self.dw = get_DockerWorker({'cap_add': ['data2']})
        self.assertTrue(self.dw.compare_cap_add(container_info))

    def test_compare_ipc_mode_neg(self):
        container_info = {'HostConfig': dict(IpcMode='data')}
        self.dw = get_DockerWorker({'ipc_mode': 'data'})
        self.assertFalse(self.dw.compare_ipc_mode(container_info))

    def test_compare_ipc_mode_pos(self):
        container_info = {'HostConfig': dict(IpcMode='data1')}
        self.dw = get_DockerWorker({'ipc_mode': 'data2'})
        self.assertTrue(self.dw.compare_ipc_mode(container_info))

    def test_compare_security_opt_neg(self):
        container_info = {'HostConfig': dict(SecurityOpt=['data'])}
        self.dw = get_DockerWorker({'security_opt': ['data']})
        self.assertFalse(self.dw.compare_security_opt(container_info))

    def test_compare_security_opt_pos(self):
        container_info = {'HostConfig': dict(SecurityOpt=['data1'])}
        self.dw = get_DockerWorker({'security_opt': ['data2']})
        self.assertTrue(self.dw.compare_security_opt(container_info))

    def test_compare_pid_mode_neg(self):
        container_info = {'HostConfig': dict(PidMode='host')}
        self.dw = get_DockerWorker({'pid_mode': 'host'})
        self.assertFalse(self.dw.compare_pid_mode(container_info))

    def test_compare_pid_mode_pos(self):
        container_info = {'HostConfig': dict(PidMode='host1')}
        self.dw = get_DockerWorker({'pid_mode': 'host2'})
        self.assertTrue(self.dw.compare_pid_mode(container_info))

    def test_compare_privileged_neg(self):
        container_info = {'HostConfig': dict(Privileged=True)}
        self.dw = get_DockerWorker({'privileged': True})
        self.assertFalse(self.dw.compare_privileged(container_info))

    def test_compare_privileged_pos(self):
        container_info = {'HostConfig': dict(Privileged=True)}
        self.dw = get_DockerWorker({'privileged': False})
        self.assertTrue(self.dw.compare_privileged(container_info))

    def test_compare_labels_neg(self):
        container_info = {'Config': dict(Labels={'kolla_version': '2.0.1'})}
        self.dw = get_DockerWorker({'labels': {'kolla_version': '2.0.1'}})
        self.dw.check_image = mock.MagicMock(return_value=dict(
            Labels={'kolla_version': '2.0.1'}))
        self.assertFalse(self.dw.compare_labels(container_info))

    def test_compare_labels_pos(self):
        container_info = {'Config': dict(Labels={'kolla_version': '1.0.1'})}
        self.dw = get_DockerWorker({'labels': {'kolla_version': '2.0.1'}})
        self.dw.check_image = mock.MagicMock(return_value=dict(
            Labels={'kolla_version': '1.0.1'}))
        self.assertTrue(self.dw.compare_labels(container_info))

    def test_compare_volumes_from_neg(self):
        container_info = {'HostConfig': dict(VolumesFrom=['777f7dc92da7'])}
        self.dw = get_DockerWorker({'volumes_from': ['777f7dc92da7']})

        self.assertFalse(self.dw.compare_volumes_from(container_info))

    def test_compare_volumes_from_post(self):
        container_info = {'HostConfig': dict(VolumesFrom=['777f7dc92da7'])}
        self.dw = get_DockerWorker({'volumes_from': ['ba8c0c54f0f2']})

        self.assertTrue(self.dw.compare_volumes_from(container_info))

    def test_compare_volumes_neg(self):
        container_info = {
            'Config': dict(Volumes=['/var/log/kolla/']),
            'HostConfig': dict(Binds=['kolla_logs:/var/log/kolla/:rw'])}
        self.dw = get_DockerWorker(
            {'volumes': ['kolla_logs:/var/log/kolla/:rw']})

        self.assertFalse(self.dw.compare_volumes(container_info))

    def test_compare_volumes_pos(self):
        container_info = {
            'Config': dict(Volumes=['/var/log/kolla/']),
            'HostConfig': dict(Binds=['kolla_logs:/var/log/kolla/:rw'])}
        self.dw = get_DockerWorker(
            {'volumes': ['/dev/:/dev/:rw']})

        self.assertTrue(self.dw.compare_volumes(container_info))

    def test_compare_environment_neg(self):
        container_info = {'Config': dict(
            Env=['KOLLA_CONFIG_STRATEGY=COPY_ALWAYS',
                 'KOLLA_BASE_DISTRO=ubuntu',
                 'KOLLA_INSTALL_TYPE=binary']
        )}
        self.dw = get_DockerWorker({
            'environment': dict(KOLLA_CONFIG_STRATEGY='COPY_ALWAYS',
                                KOLLA_BASE_DISTRO='ubuntu',
                                KOLLA_INSTALL_TYPE='binary')})

        self.assertFalse(self.dw.compare_environment(container_info))

    def test_compare_environment_pos(self):
        container_info = {'Config': dict(
            Env=['KOLLA_CONFIG_STRATEGY=COPY_ALWAYS',
                 'KOLLA_BASE_DISTRO=ubuntu',
                 'KOLLA_INSTALL_TYPE=binary']
        )}
        self.dw = get_DockerWorker({
            'environment': dict(KOLLA_CONFIG_STRATEGY='COPY_ALWAYS',
                                KOLLA_BASE_DISTRO='centos',
                                KOLLA_INSTALL_TYPE='binary')})

        self.assertTrue(self.dw.compare_environment(container_info))
