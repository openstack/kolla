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

import abc
import os
import sys

from mock import patch
from oslo_log import fixture as log_fixture
from oslo_log import log as logging
from oslotest import base
import six
import testtools

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools')))
from kolla.cmd import build

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BuildTest(object):
    excluded_images = abc.abstractproperty()

    def setUp(self):
        super(BuildTest, self).setUp()
        self.useFixture(log_fixture.SetLogLevel([__name__],
                                                logging.logging.INFO))
        self.build_args = [__name__, "--debug", '--threads', '4']

    @testtools.skipUnless(os.environ.get('DOCKER_BUILD_TEST'),
                          'Skip the docker build test')
    def runTest(self):
        with patch.object(sys, 'argv', self.build_args):
            LOG.info("Running with args %s", self.build_args)
            bad_results, good_results, unmatched_results = build.main()

        failures = 0
        for image, result in six.iteritems(bad_results):
            if image in self.excluded_images:
                if result is 'error':
                    continue
                failures = failures + 1
                LOG.warning(">>> Expected image '%s' to fail, please update"
                            " the excluded_images in source file above if the"
                            " image build has been fixed.", image)
            else:
                if result is not 'error':
                    continue
                failures = failures + 1
                LOG.critical(">>> Expected image '%s' to succeed!", image)

        for image in unmatched_results.keys():
            LOG.warning(">>> Image '%s' was not matched", image)

        self.assertEqual(failures, 0, "%d failure(s) occurred" % failures)


class BuildTestCentosBinary(BuildTest, base.BaseTestCase):
    excluded_images = ["murano-base",
                       "ironic-pxe",
                       "ironic-inspector",
                       "mistral-base",
                       "murano-base"]

    def setUp(self):
        super(BuildTestCentosBinary, self).setUp()
        self.build_args.extend(["--base", "centos",
                                "--type", "binary",
                                "--tag", "1.1.0"])


class BuildTestCentosSource(BuildTest, base.BaseTestCase):
    excluded_images = ["gnocchi-base",
                       "murano-base",
                       "ironic-pxe",
                       "ironic-inspector",
                       "mistral-base"]

    def setUp(self):
        super(BuildTestCentosSource, self).setUp()
        self.build_args.extend(["--base", "centos",
                                "--type", "source",
                                "--tag", "1.1.0"])


class BuildTestUbuntuBinary(BuildTest, base.BaseTestCase):
    excluded_images = ["mistral-base",
                       "magnum-base",
                       "zaqar"]

    def setUp(self):
        super(BuildTestUbuntuBinary, self).setUp()
        self.build_args.extend(["--base", "ubuntu",
                                "--type", "binary",
                                "--tag", "1.1.0"])


class BuildTestUbuntuSource(BuildTest, base.BaseTestCase):
    excluded_images = []

    def setUp(self):
        super(BuildTestUbuntuSource, self).setUp()
        self.build_args.extend(["--base", "ubuntu",
                                "--type", "source",
                                "--tag", "1.1.0"])


class BuildTestOracleLinuxBinary(BuildTest, base.BaseTestCase):
    excluded_images = ["murano-base",
                       "ironic-pxe",
                       "ironic-inspector",
                       "mistral-base",
                       "murano-base"]

    def setUp(self):
        super(BuildTestOracleLinuxBinary, self).setUp()
        self.build_args.extend(["--base", "oraclelinux",
                                "--type", "binary",
                                "--tag", "1.1.0"])


class BuildTestOracleLinuxSource(BuildTest, base.BaseTestCase):
    excluded_images = []

    def setUp(self):
        super(BuildTestOracleLinuxSource, self).setUp()
        self.build_args.extend(["--base", "oraclelinux",
                                "--type", "source",
                                "--tag", "1.1.0"])


class DeployTestCentosBinary(BuildTestCentosBinary):
    def setUp(self):
        super(DeployTestCentosBinary, self).setUp()
        self.build_args.extend(["--profile", "gate"])


class DeployTestCentosSource(BuildTestCentosSource):
    def setUp(self):
        super(DeployTestCentosSource, self).setUp()
        self.build_args.extend(["--profile", "gate"])


class DeployTestOracleLinuxBinary(BuildTestOracleLinuxBinary):
    def setUp(self):
        super(DeployTestOracleLinuxBinary, self).setUp()
        self.build_args.extend(["--profile", "gate"])


class DeployTestOracleLinuxSource(BuildTestOracleLinuxSource):
    def setUp(self):
        super(DeployTestOracleLinuxSource, self).setUp()
        self.build_args.extend(["--profile", "gate"])


class DeployTestUbuntuBinary(BuildTestUbuntuBinary):
    def setUp(self):
        super(DeployTestUbuntuBinary, self).setUp()
        self.build_args.extend(["--profile", "gate"])


class DeployTestUbuntuSource(BuildTestUbuntuSource):
    def setUp(self):
        super(DeployTestUbuntuSource, self).setUp()
        self.build_args.extend(["--profile", "gate"])
