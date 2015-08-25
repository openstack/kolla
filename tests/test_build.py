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


from mock import patch
from os import path
from oslo_log import fixture as log_fixture
from oslo_log import log as logging
from oslotest import base

import sys
sys.path.append(path.abspath(path.join(path.dirname(__file__), '../tools')))
from kolla.cmd import build

LOG = logging.getLogger(__name__)


class BuildTest(base.BaseTestCase):

    def setUp(self):
        super(BuildTest, self).setUp()
        self.useFixture(log_fixture.SetLogLevel([__name__],
                                                logging.logging.INFO))
        self.build_args = [__name__, "--debug"]

    def runTest(self):
        with patch.object(sys, 'argv', self.build_args):
            LOG.info("Running with args %s" % self.build_args)
            bad_results, good_results = build.main()

        # these are images that are known to not build properly
        excluded_images = ["gnocchi-api",
                           "gnocchi-statsd"]

        failures = 0
        for image, result in bad_results.iteritems():
            if image in excluded_images:
                if result is 'error':
                    continue
                failures = failures + 1
                LOG.warning(">>> Expected image '%s' to fail, please update"
                            " the excluded_images in source file above if the"
                            " image build has been fixed." % image)
            else:
                if result is not 'error':
                    continue
                failures = failures + 1
                LOG.critical(">>> Expected image '%s' to succeed!" % image)

        self.assertEqual(failures, 0, "%d failure(s) occurred" % failures)


class BuildTestCentosBinaryDocker(BuildTest):
    def setUp(self):
        super(BuildTestCentosBinaryDocker, self).setUp()
        self.build_args.extend(["--base", "centos",
                                "--type", "binary"])


class BuildTestCentosSourceDocker(BuildTest):
    def setUp(self):
        super(BuildTestCentosSourceDocker, self).setUp()
        self.build_args.extend(["--base", "centos",
                                "--type", "source"])


class BuildTestUbuntuSourceDocker(BuildTest):
    def setUp(self):
        super(BuildTestUbuntuSourceDocker, self).setUp()
        self.build_args.extend(["--base", "ubuntu",
                                "--type", "source"])


class BuildTestCentosBinaryTemplate(BuildTest):
    def setUp(self):
        super(BuildTestCentosBinaryTemplate, self).setUp()
        self.build_args.extend(["--base", "centos",
                                "--type", "binary",
                                "--template"])


class BuildTestCentosSourceTemplate(BuildTest):
    def setUp(self):
        super(BuildTestCentosSourceTemplate, self).setUp()
        self.build_args.extend(["--base", "centos",
                                "--type", "source",
                                "--template"])


class BuildTestUbuntuSourceTemplate(BuildTest):
    def setUp(self):
        super(BuildTestUbuntuSourceTemplate, self).setUp()
        self.build_args.extend(["--base", "ubuntu",
                                "--type", "source",
                                "--template"])
