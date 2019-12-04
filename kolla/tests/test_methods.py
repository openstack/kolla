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

from kolla.template import methods
from kolla.tests import base


class MethodsTest(base.TestCase):

    def test_debian_package_install(self):
        packages = ['https://packages.debian.org/package1.deb', 'package2.deb']
        result = methods.debian_package_install(packages)
        expectCmd = 'apt-get -y install --no-install-recommends package2.deb'
        self.assertEqual(expectCmd, result.split("&&")[1].strip())

    def test_enable_repos_rhel(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'rhel',
            'base_package_type': 'rpm',
            'distro_package_manager': 'yum'
        }

        result = methods.enable_repos(template_vars, ['grafana'])
        expectCmd = ''
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'centos',
            'base_package_type': 'rpm',
            'distro_package_manager': 'yum'
        }

        result = methods.enable_repos(template_vars, ['grafana'])
        expectCmd = 'RUN yum-config-manager  --enable grafana'
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_missing_repo(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'centos',
            'base_package_type': 'rpm',
            'distro_package_manager': 'yum'
        }

        result = methods.enable_repos(template_vars, ['missing_repo'])
        expectCmd = ''
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_multiple(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'centos',
            'base_package_type': 'rpm',
            'distro_package_manager': 'yum'
        }

        result = methods.enable_repos(template_vars, ['grafana', 'ceph'])
        expectCmd = 'RUN yum-config-manager  --enable grafana '
        expectCmd += '--enable centos-ceph-nautilus'
        self.assertEqual(expectCmd, result)

    def test_enable_repos_debian(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb'
        }

        result = methods.enable_repos(template_vars, ['grafana'])
        expectCmd = 'RUN echo "deb https://packages.grafana.com/oss/deb '
        expectCmd += 'stable main" >/etc/apt/sources.list.d/grafana.list'
        self.assertEqual(expectCmd, result)

    def test_enable_repos_debian_missing_repo(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb'
        }

        result = methods.enable_repos(template_vars, ['missing_repo'])
        expectCmd = ''
        self.assertEqual(expectCmd, result)

    def test_enable_repos_debian_multiple(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb'
        }

        result = methods.enable_repos(template_vars, ['grafana', 'kibana'])
        expectCmd = 'RUN echo "deb https://packages.grafana.com/oss/deb '
        expectCmd += 'stable main" >/etc/apt/sources.list.d/grafana.list && '
        expectCmd += 'echo "deb [arch=amd64] '
        expectCmd += 'https://artifacts.elastic.co/packages/5.x/apt stable '
        expectCmd += 'main" >/etc/apt/sources.list.d/kibana.list'
        self.assertEqual(expectCmd, result)
