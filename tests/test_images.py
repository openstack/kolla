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

import testtools
from subprocess import check_output

class ImagesTest(testtools.TestCase):
    def setUp(self):
        super(ImagesTest, self).setUp()

    def test_builds(self):
        build_output = check_output(["tools/build-all-docker-images",
                                    "--release",
                                    "--pull",
                                    "--testmode"])

        # these are images that are known to not build properly
        excluded_images = ["kollaglue/centos-rdo-swift-proxy-server",
                           "kollaglue/centos-rdo-swift-container",
                           "kollaglue/centos-rdo-swift-base",
                           "kollaglue/centos-rdo-swift-account",
                           "kollaglue/centos-rdo-swift-object",
                           "kollaglue/centos-rdo-barbican",
                           "kollaglue/fedora-rdo-base",
                           "kollaglue/centos-rdo-rhel-osp-base"]

        results = eval(build_output.splitlines()[-1])

        for image, result in results.iteritems():
            if image in excluded_images:
                self.assertEqual(result, 'fail')
            else:
                self.assertNotEqual(result, 'fail')
