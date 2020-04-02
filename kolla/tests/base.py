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

import os
from unittest import mock

import fixtures
from oslo_config import cfg
from oslotest import base as oslotest_base

from kolla.common import config as common_config


TESTS_ROOT = os.path.dirname(os.path.abspath(__file__))


class TestCase(oslotest_base.BaseTestCase):
    '''All unit test should inherit from this class'''
    config_file = None

    def setUp(self):
        super(TestCase, self).setUp()
        self.conf = cfg.ConfigOpts()
        default_config_files = self.get_default_config_files()
        common_config.parse(self.conf, [],
                            default_config_files=default_config_files)
        # NOTE(jeffrey4l): mock the _get_image_dir method to return a fake
        # docker images dir
        self.useFixture(fixtures.MockPatch(
            'kolla.image.build.KollaWorker._get_images_dir',
            mock.Mock(return_value=os.path.join(TESTS_ROOT, 'docker'))))

    def get_default_config_files(self):
        if self.config_file:
            return [os.path.join(TESTS_ROOT, 'etc', self.config_file)]
