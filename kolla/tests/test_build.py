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
import sys

from kolla.cmd import build as build_cmd
from kolla import exception
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
FAKE_IMAGE_CHILD_UNMATCHED = build.Image(
    'image-child-unmatched', 'image-child-unmatched:latest',
    '/fake/path3', parent_name='image-base',
    parent=FAKE_IMAGE, status=build.STATUS_UNMATCHED)
FAKE_IMAGE_CHILD_ERROR = build.Image(
    'image-child-error', 'image-child-error:latest',
    '/fake/path4', parent_name='image-base',
    parent=FAKE_IMAGE, status=build.STATUS_ERROR)
FAKE_IMAGE_CHILD_BUILT = build.Image(
    'image-child-built', 'image-child-built:latest',
    '/fake/path5', parent_name='image-base',
    parent=FAKE_IMAGE, status=build.STATUS_BUILT)


class TasksTest(base.TestCase):

    def setUp(self):
        super(TasksTest, self).setUp()
        self.image = FAKE_IMAGE.copy()
        # NOTE(jeffrey4l): use a real, temporary dir
        self.image.path = self.useFixture(fixtures.TempDir()).path
        self.imageChild = FAKE_IMAGE_CHILD.copy()
        # NOTE(mandre) we want the local copy of FAKE_IMAGE as the parent
        self.imageChild.parent = self.image
        self.imageChild.path = self.useFixture(fixtures.TempDir()).path

    @mock.patch('docker.version', '2.7.0')
    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.APIClient')
    def test_push_image_before_v3_0_0(self, mock_client):
        self.dc = mock_client
        pusher = build.PushTask(self.conf, self.image)
        pusher.run()
        mock_client().push.assert_called_once_with(
            self.image.canonical_name, decode=True,
            stream=True, insecure_registry=True)

    @mock.patch('docker.version', '3.0.0')
    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.APIClient')
    def test_push_image(self, mock_client):
        self.dc = mock_client
        pusher = build.PushTask(self.conf, self.image)
        pusher.run()
        mock_client().push.assert_called_once_with(
            self.image.canonical_name, decode=True, stream=True)

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.APIClient')
    def test_build_image(self, mock_client):
        self.dc = mock_client
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name, decode=True,
            network_mode=None, nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=None)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.APIClient')
    def test_build_image_with_network_mode(self, mock_client):
        self.dc = mock_client
        push_queue = mock.Mock()
        self.conf.set_override('network_mode', 'host')

        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name, decode=True,
            network_mode='host', nocache=False, rm=True, pull=True,
            forcerm=True, buildargs=None)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.APIClient')
    def test_build_image_with_build_arg(self, mock_client):
        self.dc = mock_client
        build_args = {
            'HTTP_PROXY': 'http://localhost:8080',
            'NO_PROXY': '127.0.0.1'
        }
        self.conf.set_override('build_args', build_args)
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name, decode=True,
            network_mode=None, nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, {'http_proxy': 'http://FROM_ENV:8080'},
                     clear=True)
    @mock.patch('docker.APIClient')
    def test_build_arg_from_env(self, mock_client):
        push_queue = mock.Mock()
        self.dc = mock_client
        build_args = {
            'http_proxy': 'http://FROM_ENV:8080',
        }
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name, decode=True,
            network_mode=None, nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

        self.assertTrue(builder.success)

    @mock.patch.dict(os.environ, {'http_proxy': 'http://FROM_ENV:8080'},
                     clear=True)
    @mock.patch('docker.APIClient')
    def test_build_arg_precedence(self, mock_client):
        self.dc = mock_client
        build_args = {
            'http_proxy': 'http://localhost:8080',
        }
        self.conf.set_override('build_args', build_args)

        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        builder.run()

        mock_client().build.assert_called_once_with(
            path=self.image.path, tag=self.image.canonical_name, decode=True,
            network_mode=None, nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)

        self.assertTrue(builder.success)

    @mock.patch('docker.APIClient')
    @mock.patch('requests.get')
    def test_requests_get_timeout(self, mock_get, mock_client):
        self.dc = mock_client
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

    @mock.patch('os.utime')
    @mock.patch('shutil.copyfile')
    @mock.patch('shutil.rmtree')
    @mock.patch('docker.APIClient')
    @mock.patch('requests.get')
    def test_process_source(self, mock_get, mock_client,
                            mock_rmtree, mock_copyfile, mock_utime):
        for source in [{'source': 'http://fake/source1', 'type': 'url',
                       'name': 'fake-image-base1',
                        'reference': 'http://fake/reference1'},
                       {'source': 'http://fake/source2', 'type': 'git',
                       'name': 'fake-image-base2',
                        'reference': 'http://fake/reference2'},
                       {'source': 'http://fake/source3', 'type': 'local',
                       'name': 'fake-image-base3',
                        'reference': 'http://fake/reference3'},
                       {'source': 'http://fake/source4', 'type': None,
                       'name': 'fake-image-base4',
                        'reference': 'http://fake/reference4'}]:
            self.image.source = source
            push_queue = mock.Mock()
            builder = build.BuildTask(self.conf, self.image, push_queue)
            get_result = builder.process_source(self.image, self.image.source)
            self.assertEqual(self.image.status, build.STATUS_ERROR)
            self.assertFalse(builder.success)
            if source['type'] != 'local':
                self.assertIsNone(get_result)
            else:
                self.assertIsNotNone(get_result)

    @mock.patch('os.path.exists')
    @mock.patch('os.utime')
    @mock.patch('shutil.rmtree')
    def test_process_git_source_existing_dir(self, mock_rmtree, mock_utime,
                                             mock_path_exists):
        source = {'source': 'http://fake/source1', 'type': 'git',
                  'name': 'fake-image1',
                  'reference': 'fake/reference1'}

        self.image.source = source
        self.image.path = "fake_image_path"
        mock_path_exists.return_value = True
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.image, push_queue)
        get_result = builder.process_source(self.image, self.image.source)

        mock_rmtree.assert_called_with(
            "fake_image_path/fake-image1-archive-fake-reference1")
        self.assertEqual(self.image.status, build.STATUS_ERROR)
        self.assertFalse(builder.success)
        self.assertIsNone(get_result)

    @mock.patch('docker.APIClient')
    def test_followups_docker_image(self, mock_client):
        self.imageChild.source = {
            'source': 'http://fake/source',
            'type': 'url',
            'name': 'fake-image-base'
        }
        self.imageChild.children.append(FAKE_IMAGE_CHILD_UNMATCHED)
        push_queue = mock.Mock()
        builder = build.BuildTask(self.conf, self.imageChild, push_queue)
        builder.success = True
        self.conf.push = FAKE_IMAGE_CHILD_UNMATCHED
        get_result = builder.followups
        self.assertEqual(1, len(get_result))


class KollaWorkerTest(base.TestCase):

    config_file = 'default.conf'

    def setUp(self):
        super(KollaWorkerTest, self).setUp()
        image = FAKE_IMAGE.copy()
        image.status = None
        image_child = FAKE_IMAGE_CHILD.copy()
        image_child.status = None
        image_unmatched = FAKE_IMAGE_CHILD_UNMATCHED.copy()
        image_error = FAKE_IMAGE_CHILD_ERROR.copy()
        image_built = FAKE_IMAGE_CHILD_BUILT.copy()
        # NOTE(mandre) we want the local copy of FAKE_IMAGE as the parent
        for i in [image_child, image_unmatched, image_error, image_built]:
            i.parent = image

        self.images = [image, image_child, image_unmatched,
                       image_error, image_built]
        patcher = mock.patch('docker.APIClient')
        self.addCleanup(patcher.stop)
        self.mock_client = patcher.start()

    def test_supported_base_type(self):
        rh_base = ['centos', 'oraclelinux', 'rhel']
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
            self.assertRaises(exception.KollaMismatchBaseTypeException,
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

        found = False
        for image in kolla.images:
            if image.name == 'neutron-server':
                for plugin in image.plugins:
                    if plugin == expected_plugin:
                        found = True
                        break
                break
        if not found:
            self.fail('Can not find the expected neutron arista plugin')

    def test_build_image_list_plugin_parsing(self):
        """Ensure regex used to parse plugins adds them to the correct image"""
        self.conf.set_override('install_type', 'source')

        kolla = build.KollaWorker(self.conf)
        kolla.setup_working_dir()
        kolla.find_dockerfiles()
        kolla.create_dockerfiles()
        kolla.build_image_list()
        for image in kolla.images:
            if image.name == 'base':
                self.assertEqual(len(image.plugins), 0,
                                 'base image should not have any plugins '
                                 'registered')
                break
        else:
            self.fail('Expected to find the base image in this test')

    def test_set_time(self):
        self.conf.set_override('install_type', 'source')
        kolla = build.KollaWorker(self.conf)
        kolla.setup_working_dir()
        kolla.set_time()

    def _get_matched_images(self, images):
        return [image for image in images
                if image.status == build.STATUS_MATCHED]

    def test_skip_parents(self):
        self.conf.set_override('regex', ['image-child'])
        self.conf.set_override('skip_parents', True)
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()

        self.assertEqual(build.STATUS_SKIPPED, kolla.images[1].parent.status)

    def test_without_profile(self):
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()

        self.assertEqual(5, len(self._get_matched_images(kolla.images)))

    def test_build_rpm_setup(self):
        """checking the length of list of docker commands"""
        self.conf.set_override('rpm_setup_config', ["a.rpm", "b.repo"])
        kolla = build.KollaWorker(self.conf)
        self.assertEqual(2, len(kolla.rpm_setup))

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

    @mock.patch('json.dump')
    def test_list_dependencies(self, dump_mock):
        self.conf.set_override('profile', ['all'])
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.filter_images()
        kolla.list_dependencies()
        dump_mock.assert_called_once_with(mock.ANY, sys.stdout, indent=2)

    def test_summary(self):
        kolla = build.KollaWorker(self.conf)
        kolla.images = self.images
        kolla.image_statuses_good['good'] = None
        kolla.image_statuses_bad['bad'] = None
        kolla.image_statuses_unmatched['unmatched'] = None
        results = kolla.summary()
        self.assertIsNone(results['failed'][0]['status'])

    @mock.patch('shutil.copytree')
    def test_work_dir(self, copytree_mock):
        self.conf.set_override('work_dir', 'tmp/foo')
        kolla = build.KollaWorker(self.conf)
        kolla.setup_working_dir()
        self.assertEqual('tmp/foo/docker', kolla.working_dir)


class MainTest(base.TestCase):

    @mock.patch.object(build, 'run_build')
    def test_images_built(self, mock_run_build):
        image_statuses = ({}, {'img': 'built'}, {}, {})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(0, result)

    @mock.patch.object(build, 'run_build')
    def test_images_unmatched(self, mock_run_build):
        image_statuses = ({}, {}, {'img': 'unmatched'}, {})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(0, result)

    @mock.patch.object(build, 'run_build')
    def test_no_images_built(self, mock_run_build):
        mock_run_build.return_value = None
        result = build_cmd.main()
        self.assertEqual(0, result)

    @mock.patch.object(build, 'run_build')
    def test_bad_images(self, mock_run_build):
        image_statuses = ({'img': 'error'}, {}, {}, {})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(1, result)

    @mock.patch('sys.argv')
    @mock.patch('docker.APIClient')
    def test_run_build(self, mock_client, mock_sys):
        result = build.run_build()
        self.assertTrue(result)

    @mock.patch.object(build, 'run_build')
    def test_skipped_images(self, mock_run_build):
        image_statuses = ({}, {}, {}, {'img': 'skipped'})
        mock_run_build.return_value = image_statuses
        result = build_cmd.main()
        self.assertEqual(0, result)
