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

import importlib.util
import os.path
import sys

import fixtures
from oslotest import base


def load_module(name, path):
    module_spec = importlib.util.spec_from_file_location(
        name, path
    )
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


# kolla_package_report is an Ansible module in a role, not part of the kolla
# package, so load it by path.
this_dir = os.path.dirname(sys.modules[__name__].__file__)
kolla_package_report = load_module(
    'kolla_package_report',
    os.path.join(this_dir, '..', 'roles', 'kolla-build-tests', 'library',
                 'kolla_package_report.py'))


class ParseParentTest(base.BaseTestCase):

    def test_buildkit(self):
        self.assertEqual('nova-base', kolla_package_report.parse_parent([
            'INFO:kolla.common.utils.nova-api:#2 [internal] load metadata '
            'for docker.io/kolla/nova-base:master-rocky-10\n',
            'INFO:kolla.common.utils.nova-api:#4 [1/7] FROM '
            'docker.io/kolla/nova-base:master-rocky-10@sha256:00\n']))

    def test_buildkit_padded(self):
        self.assertEqual('openstack-base', kolla_package_report.parse_parent([
            'INFO:kolla.common.utils.nova-base:#5 [ 1/23] FROM '
            'docker.io/kolla/openstack-base:master-rocky-10@sha256:00\n']))

    def test_podman(self):
        self.assertEqual('openstack-base', kolla_package_report.parse_parent([
            'INFO:kolla.common.utils.nova-base:STEP 1/15: FROM '
            'kolla/openstack-base:master-rocky-10\n']))

    def test_external_base(self):
        self.assertEqual('rockylinux', kolla_package_report.parse_parent([
            'INFO:kolla.common.utils.base:#5 [ 1/23] FROM '
            'quay.io/rockylinux/rockylinux:10@sha256:00\n']))

    def test_no_from(self):
        self.assertIsNone(kolla_package_report.parse_parent([
            'INFO:kolla.common.utils.base:Building started\n',
            'INFO:kolla.common.utils.base:#5 ' + 'x' * 200000 + '\n']))


class AnalyseTest(base.BaseTestCase):

    PARENTS = {'base': None, 'openstack-base': 'base',
               'nova-base': 'openstack-base', 'nova-api': 'nova-base',
               'nova-compute': 'nova-base', 'cinder-base': 'openstack-base'}

    def setUp(self):
        super().setUp()
        tmp = self.useFixture(fixtures.TempDir()).path
        self.logdir = os.path.join(tmp, 'build')
        self.pkgdir = os.path.join(tmp, 'packages')
        os.mkdir(self.logdir)
        os.mkdir(self.pkgdir)

    def _image(self, image, parent, packages=None):
        with open(os.path.join(self.logdir, image + '.log'), 'w') as f:
            f.write('INFO:kolla.common.utils.%s:#4 [1/3] FROM '
                    'docker.io/kolla/%s:master-rocky-10@sha256:00\n' %
                    (image, parent))
        if packages is not None:
            with open(os.path.join(self.pkgdir, image + '.txt'), 'w') as f:
                f.write(''.join(p + '\n' for p in packages))

    def test_common_parent(self):
        self.assertEqual('nova-base', kolla_package_report.common_parent(
            ['nova-api', 'nova-compute'], self.PARENTS))
        self.assertEqual('openstack-base', kolla_package_report.common_parent(
            ['nova-api', 'cinder-base'], self.PARENTS))
        self.assertIsNone(kolla_package_report.common_parent(
            ['base', 'nova-api'], self.PARENTS))

    def test_analyse(self):
        self._image('base', 'rockylinux', ['bash', 'libbar', 'gpg-pubkey'])
        self._image('openstack-base', 'base', ['bash', 'git'])
        self._image('nova-base', 'openstack-base', ['bash', 'git', 'libnl3'])
        self._image('cinder-base', 'openstack-base', ['bash', 'git', 'libnl3'])
        self._image('nova-api', 'nova-base',
                    ['bash', 'git', 'libnl3', 'libbar', 'libfoo'])
        self._image('nova-compute', 'nova-base',
                    ['bash', 'git', 'libnl3', 'libfoo', 'gpg-pubkey'])

        report = kolla_package_report.analyse(self.logdir, self.pkgdir, 1)

        self.assertEqual(
            [{'package': 'libbar',
              'images': ['base', 'nova-api'],
              'suggested_parent': None},
             {'package': 'libfoo',
              'images': ['nova-api', 'nova-compute'],
              'suggested_parent': 'nova-base'},
             {'package': 'libnl3',
              'images': ['cinder-base', 'nova-base'],
              'suggested_parent': 'openstack-base'}],
            report['candidates'])
        self.assertEqual(
            [{'image': 'openstack-base', 'parent': 'base',
              'packages': ['libbar']}],
            report['removals'])
        self.assertEqual([], report['skipped'])
        self.assertEqual(
            ['libbar is installed by 2 images separately, but they have no '
             'common parent image',
             'libfoo is installed by 2 images separately; consider '
             'installing it once in nova-base instead',
             'libnl3 is installed by 2 images separately; consider '
             'installing it once in openstack-base instead',
             'openstack-base removes libbar, which its parent base has '
             'installed'],
            report['warnings'])
        self.assertEqual([], kolla_package_report.analyse(
            self.logdir, self.pkgdir, 2)['candidates'])

    def test_parent_without_package_list_skipped(self):
        self._image('base', 'rockylinux', ['bash'])
        self._image('openstack-base', 'base')
        self._image('nova-base', 'openstack-base', ['bash', 'git', 'libnl3'])

        report = kolla_package_report.analyse(self.logdir, self.pkgdir, 0)

        self.assertEqual(['nova-base'], report['skipped'])
        self.assertEqual(['bash'],
                         [c['package'] for c in report['candidates']])

    def test_format_report(self):
        report = {'candidates': [{'package': 'libnl3',
                                  'images': ['cinder-base', 'nova-base'],
                                  'suggested_parent': 'openstack-base'},
                                 {'package': 'libbar',
                                  'images': ['base', 'nova-api'],
                                  'suggested_parent': None}],
                  'removals': [{'image': 'cinder-volume',
                                'parent': 'cinder-base',
                                'packages': ['foo', 'bar']}],
                  'skipped': ['nova-base']}
        self.assertEqual(
            'Consider moving the following packages to a parent image:\n'
            'libnl3 -> openstack-base (cinder-base, nova-base)\n'
            'libbar -> (no common parent) (base, nova-api)\n'
            '\n'
            'Packages removed compared with the parent image:\n'
            'cinder-volume (parent cinder-base): foo, bar\n'
            '\n'
            'Skipped (parent has no package list): nova-base\n',
            kolla_package_report.format_report(report))
        self.assertEqual('', kolla_package_report.format_report(
            {'candidates': [], 'removals': [], 'skipped': []}))
