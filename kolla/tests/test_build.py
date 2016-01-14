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
import mock
import os

from kolla.cmd import build
from kolla.tests import base


FAKE_IMAGE = {
    'name': 'image-base',
    'status': 'matched',
    'parent': None,
    'path': '/fake/path',
    'plugins': [],
    'fullname': 'image-base:latest',
}


class WorkerThreadTest(base.TestCase):

    def setUp(self):
        super(WorkerThreadTest, self).setUp()
        # NOTE(jeffrey4l): use a real, temporary dir
        FAKE_IMAGE['path'] = self.useFixture(fixtures.TempDir()).path

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('docker.Client')
    def test_build_image(self, mock_client):
        queue = mock.Mock()
        push_queue = mock.Mock()
        worker = build.WorkerThread(queue,
                                    push_queue,
                                    self.conf)
        worker.builder(FAKE_IMAGE)

        mock_client().build.assert_called_once_with(
            path=FAKE_IMAGE['path'], tag=FAKE_IMAGE['fullname'],
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
        worker.builder(FAKE_IMAGE)

        mock_client().build.assert_called_once_with(
            path=FAKE_IMAGE['path'], tag=FAKE_IMAGE['fullname'],
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
        worker.builder(FAKE_IMAGE)

        mock_client().build.assert_called_once_with(
            path=FAKE_IMAGE['path'], tag=FAKE_IMAGE['fullname'],
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
        worker.builder(FAKE_IMAGE)

        mock_client().build.assert_called_once_with(
            path=FAKE_IMAGE['path'], tag=FAKE_IMAGE['fullname'],
            nocache=False, rm=True, pull=True, forcerm=True,
            buildargs=build_args)
