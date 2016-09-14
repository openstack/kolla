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

from kolla.cmd import build as build_cmd
from kolla.image import build
from kolla.tests import base


FAKE_IMAGE = build.Image(
    'image-base', 'image-base:latest',
    '/fake/path', parent_name=None,
    parent=None, status=build.STATUS_MATCHED)
FAKE_IMAGE_CHILD = build.Image(
    'image-child', 'image-child:latest',
    '/fake/path2', parent_name='image-base',
    parent=FAKE_IMAGE, status=build.STATUS_MATCHED)


class TasksTest(base.TestCase):

    def setUp(self):
        super(TasksTest, self).setUp()
        self.image = FAKE_IMAGE.copy()
        # NOTE(jeffrey4l): use a real, temporary dir
        self.image.path = self.useFixture(fixtures.TempDir()).path

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.Client')
    def test_push_image(self, mock_client):
        pusher = build.PushTask(self.conf, self.image)
        pusher.run()
        mock_client().push.assert_called_once_with(
            self.image.canonical_name, stream=True, insecure_registry=True)

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.Client')
    def test_build_image(self, mock_client):
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name,
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=None)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.Client')
    def test_build_image_with_build_arg(self, mock_client):
        build_args = {
            'HTTP_PROXY': 'http://localhost:8080',
            'NO_PROXY': '127.0.0.1'
        }
        self.conf.set_override('build_args', build_args)
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name,
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, {'http_proxy': 'http://FROM_ENV:8080'},
                     clear=True)
    @mock.patch('docker.Client')
    def test_build_arg_from_env(self, mock_client):
        push_queue = mock.Mock()
        build_args = {
            'http_proxy': 'http://FROM_ENV:8080',
        }
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name,
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, {'http_proxy': 'http://FROM_ENV:8080'},
                     clear=True)
    @mock.patch('docker.Client')
    def test_build_arg_precedence(self, mock_client):
        build_args = {
            'http_proxy': 'http://localhost:8080',
        }
        self.conf.set_override('build_args', build_args)

        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name,
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

        self.assertTrue(builder.success)

    @mock.patch('docker.Client')
    @mock.patch('requests.get')
    def test_requests_get_timeout(self, mock_get, mock_client):
        self.image.source = {
            'source': 'http://fake/source',
            'type': 'url',
            'name': 'fake-image-base'
        }
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        mock_get.side_effect = requests.exceptions.Timeout
        get_result = builder.process_source(self.image, self.image.source)

        self.assertIsNone(get_result)
        self.assertEqual(self.image.status, build.STATUS_ERROR)
        mock_get.assert_called_once_with(self.image.source['source'],
                                         timeout=120)

        self.assertFalse(builder.success)


class KollaWorkerTest(base.TestCase):

    config_file = 'default.conf'

    def setUp(self):
        super(KollaWorkerTest, self).setUp()
        image = FAKE_IMAGE.copy()
        image.status = None
        image_child = FAKE_IMAGE_CHILD.copy()
        image_child.status = None
        self.images = [image, image_child]

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
            'source': 'https://git.openstack.org/openstack/networking-arista',
            'type': 'git'
        }
        for image in kolla.images:
            if image.name == 'neutron-server':
                self.assertEqual(image.plugins[0], expected_plugin)
                break
        else:
            self.fail('Can not find the expected neutron arista plugin')

    def _get_matched_images(self, images):
        return [image for image in images
                if image.status == build.STATUS_MATCHED]

    def test_without_profile(self):
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()

        self.assertEqual(2, len(self._get_matched_images(kolla.images)))

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

    @mock.patch('pprint.pprint')
    def test_list_dependencies(self, pprint_mock):
        self.conf.set_override('profile', ['all'])
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()
        kolla.list_dependencies()
        pprint_mock.assert_called_once_with(mock.ANY)


@mock.patch.object(build, 'run_build')
class MainTest(base.TestCase):

    def test_images_built(self, mock_run_build):
        image_statuses = ({}, {'img': 'built'}, {})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(0, result)

    def test_images_unmatched(self, mock_run_build):
        image_statuses = ({}, {}, {'img': 'unmatched'})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(0, result)

    def test_no_images_built(self, mock_run_build):
        mock_run_build.return_value = None
        result = build_cmd.main()
        self.assertEqual(0, result)

    def test_bad_images(self, mock_run_build):
        image_statuses = ({'img': 'error'}, {}, {})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(1, result)
