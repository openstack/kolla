#    Copyright 2016 GohighSec
#
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

import ddt

from kolla.hacking import checks
from kolla.tests import base


@ddt.ddt
class HackingTestCase(base.TestCase):
    """Hacking test cases

    This class tests the hacking checks in kolla.hacking.checks by passing
    strings to the check methods like the pep8/flake8 parser would. The parser
    loops over each line in the file and then passes the parameters to the
    check method.
    """

    def test_no_log_warn_check(self):
        self.assertEqual(0, len(list(checks.no_log_warn(
            "LOG.warning('This should not trigger LOG.warn"
            "hacking check.')"))))
        self.assertEqual(1, len(list(checks.no_log_warn(
            "LOG.warn('We should not use LOG.warn')"))))

    def test_no_mutable_default_args(self):
        self.assertEqual(1, len(list(checks.no_mutable_default_args(
            "def get_info_from_bdm(virt_type, bdm, mapping=[])"))))

        self.assertEqual(0, len(list(checks.no_mutable_default_args(
            "defined = []"))))

        self.assertEqual(0, len(list(checks.no_mutable_default_args(
            "defined, undefined = [], {}"))))
