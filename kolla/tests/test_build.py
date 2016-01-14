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
            nocache=False, rm=True, pull=True, forcerm=True)
