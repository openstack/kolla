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

from oslo_log import fixture as log_fixture
from oslo_log import log as logging
from oslotest import base

from subprocess import Popen, PIPE, STDOUT

LOG = logging.getLogger(__name__)

class ImagesTest(base.BaseTestCase):
    def setUp(self):
        super(ImagesTest, self).setUp()
        self.useFixture(log_fixture.SetLogLevel([__name__],
                        logging.logging.INFO))

    def test_builds(self):
        proc = Popen(['tools/build-all-docker-images',
                      '--testmode',
                      '--retry 3'],
                     stdout=PIPE, stderr=STDOUT, bufsize=1)
        with proc.stdout:
            for line in iter(proc.stdout.readline, b''):
                LOG.info(line.strip())
        proc.wait()

        # these are images that are known to not build properly
        excluded_images = ["kollaglue/centos-rdo-swift-base",
                           "kollaglue/centos-rdo-swift-object",
                           "kollaglue/centos-rdo-swift-proxy-server",
                           "kollaglue/centos-rdo-swift-container",
                           "kollaglue/centos-rdo-swift-account",
                           "kollaglue/centos-rdo-rhel-osp-base"]

        results = eval(line)

        failures = 0
        for image, result in results.iteritems():
            if image in excluded_images:
                if result is 'fail':
                    continue
                failures = failures + 1
                LOG.warning(">>> Expected image '%s' to fail, please update"
                            " the excluded_images in source file above if the"
                            " image build has been fixed." % image)
            else:
                if result is not 'fail':
                    continue
                failures = failures + 1
                LOG.critical(">>> Expected image '%s' to succeed!" % image)

        self.assertEqual(failures, 0, "%d failure(s) occurred" % failures)
