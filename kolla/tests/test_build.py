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

import fixtures
import itertools
import mock
import os
import requests

from kolla.cmd import build
from kolla.tests import base


FAKE_IMAGE = {
    'name': 'image-base',
    'status': 'matched',
    'parent': None,
    'parent_name': None,
    'path': '/fake/path',
    'plugins': [],
    'fullname': 'image-base:latest',
}


class WorkerThreadTest(base.TestCase):

    def setUp(self):
        super(WorkerThreadTest, self).setUp()
        self.image = FAKE_IMAGE.copy()
        # NOTE(jeffrey4l): use a real, temporary dir
        self.image['path'] = self.useFixture(fixtures.TempDir()).path

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.Client')
    def test_build_image(self, mock_client):
        queue = mock.Mock()
        push_queue = mock.Mock()
        worker = build.WorkerThread(queue,
                                    push_queue,
                                    self.conf)
        worker.builder(self.image)

        mock_client().build.assert_called_once_with(
            path=self.image['path'], tag=self.image['fullname'],
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=None)

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.Client')
    def test_build_image_with_build_arg(self, mock_client):
        build_args = {
            'HTTP_PROXY': 'http://localhost:8080',
            'NO_PROXY': '127.0.0.1'
        }
        self.conf.set_override('build_args', build_args)
        worker = build.WorkerThread(mock.Mock(),
                                    mock.Mock(),
                                    self.conf)
        worker.builder(self.image)

        mock_client().build.assert_called_once_with(
            path=self.image['path'], tag=self.image['fullname'],
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

    @mock.patch.dict(os.environ, {'http_proxy': 'http://FROM_ENV:8080'},
                     clear=True)
    @mock.patch('docker.Client')
    def test_build_arg_from_env(self, mock_client):
        build_args = {
            'http_proxy': 'http://FROM_ENV:8080',
        }
        worker = build.WorkerThread(mock.Mock(),
                                    mock.Mock(),
                                    self.conf)
        worker.builder(self.image)

        mock_client().build.assert_called_once_with(
            path=self.image['path'], tag=self.image['fullname'],
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

    @mock.patch.dict(os.environ, {'http_proxy': 'http://FROM_ENV:8080'},
                     clear=True)
    @mock.patch('docker.Client')
    def test_build_arg_precedence(self, mock_client):
        build_args = {
            'http_proxy': 'http://localhost:8080',
        }
        self.conf.set_override('build_args', build_args)
        worker = build.WorkerThread(mock.Mock(),
                                    mock.Mock(),
                                    self.conf)
        worker.builder(self.image)

        mock_client().build.assert_called_once_with(
            path=self.image['path'], tag=self.image['fullname'],
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

    @mock.patch('docker.Client')
    @mock.patch('requests.get')
    def test_requests_get_timeout(self, mock_get, mock_client):
        worker = build.WorkerThread(mock.Mock(),
                                    mock.Mock(),
                                    self.conf)
        self.image['source'] = {
            'source': 'http://fake/source',
            'type': 'url',
            'name': 'fake-image-base'
        }
        mock_get.side_effect = requests.exceptions.Timeout
        get_result = worker.process_source(self.image,
                                           self.image['source'])

        self.assertIsNone(get_result)
        self.assertEqual(self.image['status'], 'error')
        self.assertEqual(self.image['logs'], str())
        mock_get.assert_called_once_with(self.image['source']['source'],
                                         timeout=120)


class KollaWorkerTest(base.TestCase):

    config_file = 'default.conf'

    def setUp(self):
        super(KollaWorkerTest, self).setUp()
        image = FAKE_IMAGE.copy()
        image['status'] = None
        self.images = [image]

    def test_supported_base_type(self):
        rh_base = ['fedora', 'centos', 'oraclelinux', 'rhel']
        rh_type = ['source', 'binary', 'rdo', 'rhos']
        deb_base = ['ubuntu', 'debian']
        deb_type = ['source', 'binary']

        for base_distro, install_type in itertools.chain(
                itertools.product(rh_base, rh_type),
                itertools.product(deb_base, deb_type)):
            self.conf.set_override('base', base_distro)
            self.conf.set_override('install_type', install_type)
            # should no exception raised
            build.KollaWorker(self.conf)

    def test_unsupported_base_type(self):
        for base_distro, install_type in itertools.product(
                ['ubuntu', 'debian'], ['rdo', 'rhos']):
            self.conf.set_override('base', base_distro)
            self.conf.set_override('install_type', install_type)
            self.assertRaises(build.KollaMismatchBaseTypeException,
                              build.KollaWorker, self.conf)

    def test_build_image_list_adds_plugins(self):

        self.conf.set_override('install_type', 'source')

        kolla = build.KollaWorker(self.conf)
        kolla.setup_working_dir()
        kolla.find_dockerfiles()
        kolla.create_dockerfiles()
        kolla.build_image_list()
        expected_plugin = {
            'name': 'neutron-server-plugin-networking-arista',
            'reference': 'master',
            'source': 'https://github.com/openstack/networking-arista',
            'type': 'git'
        }
        for image in kolla.images:
            if image['name'] == 'neutron-server':
                self.assertEqual(image['plugins'][0], expected_plugin)
                break
        else:
            self.fail('Can not find the expected neutron arista plugin')

    def _get_matched_images(self, images):
        return [image for image in images if image['status'] == 'matched']

    def test_without_profile(self):
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()

        self.assertEqual(1, len(self._get_matched_images(kolla.images)))

    def test_pre_defined_exist_profile(self):
        # default profile include the fake image: image-base
        self.conf.set_override('profile', ['default'])
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()

        self.assertEqual(1, len(self._get_matched_images(kolla.images)))

    def test_pre_defined_exist_profile_not_include(self):
        # infra profile do not include the fake image: image-base
        self.conf.set_override('profile', ['infra'])
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()

        self.assertEqual(0, len(self._get_matched_images(kolla.images)))

    def test_pre_defined_not_exist_profile(self):
        # NOTE(jeffrey4l): not exist profile will raise ValueError
        self.conf.set_override('profile', ['not_exist'])
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        self.assertRaises(ValueError,
                          kolla.filter_images)
