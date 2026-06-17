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
import tempfile

import yaml

from kolla.template import methods
from kolla.tests import base


class MethodsTest(base.TestCase):

    def test_debian_package_install(self):
        packages = ['https://packages.debian.org/package1.deb', 'package2.deb']
        result = methods.debian_package_install(packages)
        expectCmd = 'apt-get -y install --no-install-recommends package2.deb'
        self.assertEqual(expectCmd, result.split("&&")[1].strip())

    def test_enable_repos_centos_baseurl(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'centos',
            'base_package_type': 'rpm',
        }

        result = methods.handle_repos(template_vars, ["grafana"], "enable")
        expectCmd = "RUN grep -rlF '[grafana]' /etc/yum.repos.d/ "
        expectCmd += "2>/dev/null | xargs -r rm -f && "
        expectCmd += "echo '[grafana]' "
        expectCmd += ">/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'name=grafana' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'enabled=1' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'gpgkey=https://rpm.grafana.com/gpg.key' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'baseurl=https://rpm.grafana.com' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_ceph_distro(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'centos',
            'base_package_type': 'rpm',
        }

        result = methods.handle_repos(template_vars, ["ceph"], "enable")
        expectCmd = "RUN dnf config-manager --enable centos-ceph-squid || true"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_arch(self):
        template_vars = {
            "base_arch": "aarch64",
            "base_distro": "centos",
            "base_package_type": "rpm",
        }

        result = methods.handle_repos(template_vars, ["grafana"], "enable")
        expectCmd = "RUN grep -rlF '[grafana]' /etc/yum.repos.d/ "
        expectCmd += "2>/dev/null | xargs -r rm -f && "
        expectCmd += "echo '[grafana]' "
        expectCmd += ">/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'name=grafana' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'enabled=1' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'gpgkey=https://rpm.grafana.com/gpg.key' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'baseurl=https://rpm.grafana.com' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_multiple(self):
        template_vars = {
            "base_arch": "x86_64",
            "base_distro": "centos",
            "base_package_type": "rpm",
        }

        result = methods.handle_repos(template_vars,
                                      ["grafana", "rabbitmq"], "enable")
        expectCmd = "RUN grep -rlF '[grafana]' /etc/yum.repos.d/ "
        expectCmd += "2>/dev/null | xargs -r rm -f && "
        expectCmd += "echo '[grafana]' "
        expectCmd += ">/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'name=grafana' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'enabled=1' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'gpgkey=https://rpm.grafana.com/gpg.key' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'baseurl=https://rpm.grafana.com' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "

        expectCmd += "grep -rlF '[rabbitmq_rabbitmq-server]' "
        expectCmd += "/etc/yum.repos.d/ 2>/dev/null | xargs -r rm -f && "
        expectCmd += "echo '[rabbitmq_rabbitmq-server]' "
        expectCmd += ">/etc/yum.repos.d/rabbitmq.repo && "
        expectCmd += "echo 'name=rabbitmq_rabbitmq-server' "
        expectCmd += ">>/etc/yum.repos.d/rabbitmq.repo && "
        expectCmd += "echo 'enabled=1' "
        expectCmd += ">>/etc/yum.repos.d/rabbitmq.repo && "
        expectCmd += "echo 'gpgkey=https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-server.9F4587F226208342.key' " # noqa
        expectCmd += ">>/etc/yum.repos.d/rabbitmq.repo && "
        expectCmd += "echo '       https://github.com/rabbitmq/signing-keys/releases/download/3.0/rabbitmq-release-signing-key.asc' " # noqa
        expectCmd += ">>/etc/yum.repos.d/rabbitmq.repo && "
        expectCmd += "echo 'baseurl=https://yum1.rabbitmq.com/rabbitmq/el/9/noarch' " # noqa
        expectCmd += ">>/etc/yum.repos.d/rabbitmq.repo && "
        expectCmd += "echo 'baseurl=https://yum2.rabbitmq.com/rabbitmq/el/9/noarch' " # noqa
        expectCmd += ">>/etc/yum.repos.d/rabbitmq.repo"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_distro_enable(self):
        template_vars = {
            "base_arch": "x86_64",
            "base_distro": "centos",
            "base_package_type": "rpm",
        }

        result = methods.handle_repos(template_vars,
                                      ['crb'], 'enable')
        expectCmd = "RUN dnf config-manager --enable crb || true"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_distro_disable(self):
        template_vars = {
            "base_arch": "x86_64",
            "base_distro": "centos",
            "base_package_type": "rpm",
        }

        result = methods.handle_repos(template_vars, ['crb'], 'disable')
        expectCmd = "RUN dnf config-manager --disable crb || true"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_centos_distro_enable_multiple(self):
        template_vars = {
            "base_arch": "x86_64",
            "base_distro": "centos",
            "base_package_type": "rpm",
        }

        result = methods.handle_repos(template_vars,
                                      ['crb', 'grafana'], 'enable')
        expectCmd = "RUN dnf config-manager --enable crb || true && "
        expectCmd += "grep -rlF '[grafana]' /etc/yum.repos.d/ "
        expectCmd += "2>/dev/null | xargs -r rm -f && "
        expectCmd += "echo '[grafana]' "
        expectCmd += ">/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'name=grafana' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'enabled=1' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'gpgkey=https://rpm.grafana.com/gpg.key' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo && "
        expectCmd += "echo 'baseurl=https://rpm.grafana.com' "
        expectCmd += ">>/etc/yum.repos.d/grafana.repo"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_debian(self):
        template_vars = {
            "base_arch": "x86_64",
            "base_distro": "debian",
            "base_package_type": "deb",
            "openstack_release_codename": "Gazpacho",
        }

        result = methods.handle_repos(template_vars, ["grafana"], "enable")
        expectCmd = "RUN echo 'Uris: https://apt.grafana.com' "
        expectCmd += ">/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Components: main' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Types: deb' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Suites: stable' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Signed-By: /etc/kolla/apt-keys/grafana.asc' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_debian_arch(self):
        template_vars = {
            'base_arch': 'aarch64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
            'openstack_release_codename': 'Gazpacho',
        }

        result = methods.handle_repos(template_vars, ["rabbitmq"], "enable")
        expectCmd = "RUN echo 'Uris: https://deb1.rabbitmq.com/rabbitmq-server/debian/trixie' "  # noqa: E501
        expectCmd += ">/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Components: main' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Types: deb' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Suites: trixie' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Signed-By: /etc/kolla/apt-keys/rabbitmq.gpg' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Architectures: amd64' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources"
        self.assertEqual(expectCmd, result)

    def test_enable_repos_debian_missing_repo(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
        }

        self.assertRaises(KeyError, methods.handle_repos, template_vars,
                          ['missing_repo'], 'enable')

    def test_enable_repos_debian_multiple(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
            'openstack_release_codename': 'Gazpacho',
        }

        result = methods.handle_repos(template_vars,
                                      ['grafana', 'rabbitmq'], 'enable')
        expectCmd = "RUN echo 'Uris: https://apt.grafana.com' "
        expectCmd += ">/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Components: main' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Types: deb' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Suites: stable' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "
        expectCmd += "echo 'Signed-By: /etc/kolla/apt-keys/grafana.asc' "
        expectCmd += ">>/etc/apt/sources.list.d/grafana.sources && "

        expectCmd += "echo 'Uris: "
        expectCmd += "https://deb1.rabbitmq.com/rabbitmq-server/debian/trixie/' "  # noqa: E501
        expectCmd += ">/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Components: main' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Types: deb' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Suites: trixie' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources && "
        expectCmd += "echo 'Signed-By: /etc/kolla/apt-keys/rabbitmq.gpg' "
        expectCmd += ">>/etc/apt/sources.list.d/rabbitmq.sources"

        self.assertEqual(expectCmd, result)

    # NOTE(hrw): there is no disabling of repos for Debian/Ubuntu
    def test_disable_repos_debian(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
        }

        result = methods.handle_repos(template_vars, ["grafana"], "disable")
        expectCmd = ""
        self.assertEqual(expectCmd, result)

    def test_handle_repos_string(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
        }

        self.assertRaisesRegex(TypeError,
                               r'First argument should be a list of '
                               r'repositories',
                               methods.handle_repos, template_vars, 'grafana',
                               'disable')

    def test_enable_repos_debian_distro_noop(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
        }

        result = methods.handle_repos(template_vars, ['debian'], 'enable')
        self.assertEqual('', result)

    def test_enable_repos_deb_absolute_signed_by(self):
        repos = {'debian': {'test-repo': {
            'url': 'http://example.com/debian',
            'suite': 'trixie',
            'component': 'main',
            'gpg_key': '/usr/share/keyrings/test.gpg',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'debian',
                'base_package_type': 'deb',
                'openstack_release_codename': 'Gazpacho',
                'repos_yaml': f.name,
            }
            result = methods.handle_repos(
                template_vars, ['test-repo'], 'enable')
            self.assertIn(
                'Signed-By: /usr/share/keyrings/test.gpg', result)

    def test_repos_yaml_merge_keeps_default_repos(self):
        repos = {'rocky': {'baseos': {
            'name': 'baseos',
            'baseurl': 'http://mirror.example.com/rocky/10/BaseOS/$basearch/',
            'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'centos',
                'base_package_type': 'rpm',
                'repos_yaml': f.name,
            }
            expected_commands = methods.handle_repos(
                template_vars, ['grafana'], 'enable')
            self.assertIn(
                "echo 'gpgkey=https://rpm.grafana.com/gpg.key' "
                ">>/etc/yum.repos.d/grafana.repo",
                expected_commands)

    def test_repos_yaml_distro_override_validation(self):
        """Overriding baseos and appstream would delete rocky.repo.

        crb is a distro repo that also uses that file group. Verify a
        ValueError is raised so the user knows to override crb as well.
        """
        repos = {'rocky': {
            'baseos': {
                'name': 'baseos',
                'baseurl': 'http://mirror.example.com/rocky/10/BaseOS/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
            },
            'appstream': {
                'name': 'appstream',
                'baseurl': 'http://mirror.example.com/rocky/10/AppStream/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
            },
        }}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'rocky',
                'base_package_type': 'rpm',
                'repos_yaml': f.name,
            }
            self.assertRaisesRegex(
                ValueError, "still using distro defaults and share the same",
                methods.handle_repos, template_vars, ['baseos'], 'enable')

    def test_enable_repos_rpm_missing_url_raises(self):
        repos = {'rpm': {'test-repo': {'name': 'test-repo'}}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'centos',
                'base_package_type': 'rpm',
                'repos_yaml': f.name,
            }
            self.assertRaises(ValueError, methods.handle_repos,
                              template_vars, ['test-repo'], 'enable')

    def test_enable_repos_rpm_missing_gpgkey_raises(self):
        repos = {'rpm': {'test-repo': {
            'name': 'test-repo',
            'baseurl': 'http://mirror.example.com/repo/',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'centos',
                'base_package_type': 'rpm',
                'repos_yaml': f.name,
            }
            self.assertRaises(ValueError, methods.handle_repos,
                              template_vars, ['test-repo'], 'enable')

    def test_handle_repos_deb_build_only_backup(self):
        repos = {'debian': {'build-only-mirror': {
            'build_only': True,
            'url': 'http://mirror.example.com/debian',
            'suite': 'trixie',
            'component': 'main',
            'gpg_key': '/usr/share/keyrings/debian-archive-keyring.gpg',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'debian',
                'base_package_type': 'deb',
                'openstack_release_codename': 'Gazpacho',
                'repos_yaml': fname,
            }
            result = methods.handle_repos(
                template_vars, ['build-only-mirror'], 'enable')
            self.assertIn('mkdir -p /tmp/kolla-repos-backup', result)
            self.assertIn(
                'cp /etc/apt/sources.list.d/build-only-mirror.sources'
                ' /tmp/kolla-repos-backup/build-only-mirror.sources',
                result)
            self.assertIn(
                'touch /tmp/kolla-repos-backup/build-only-mirror.enabled',
                result)
            # backup must precede the actual repo write
            self.assertLess(
                result.index('cp /etc/apt/sources.list.d/build-only-mirror'),
                result.index("echo 'Uris:"))
        finally:
            os.unlink(fname)

    def test_handle_repos_rpm_build_only_backup(self):
        repos = {'rpm': {'build-only-mirror': {
            'build_only': True,
            'name': 'build-only-mirror',
            'baseurl': 'http://mirror.example.com/rpm/',
            'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'centos',
                'base_package_type': 'rpm',
                'repos_yaml': fname,
            }
            result = methods.handle_repos(
                template_vars, ['build-only-mirror'], 'enable')
            self.assertIn('mkdir -p /tmp/kolla-repos-backup', result)
            self.assertIn(
                'cp /etc/yum.repos.d/build-only-mirror.repo'
                ' /tmp/kolla-repos-backup/build-only-mirror.repo',
                result)
            self.assertIn(
                'touch /tmp/kolla-repos-backup/build-only-mirror.repo'
                '.enabled',
                result)
            # backup must precede DNF_REMOVE_EXISTING
            self.assertLess(
                result.index(
                    'cp /etc/yum.repos.d/build-only-mirror.repo'),
                result.index('grep -rlF'))
        finally:
            os.unlink(fname)

    def test_handle_repos_rpm_shared_file_group_backup(self):
        """Repos sharing a file_group back up that file once, by its name.

        e.g. Rocky's baseos/appstream/crb all live in rocky.repo.
        """
        repos = {'rpm': {
            'shared-a': {
                'build_only': True,
                'file_group': 'shared.repo',
                'name': 'shared-a',
                'baseurl': 'http://mirror.example.com/a/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-a',
            },
            'shared-b': {
                'build_only': True,
                'file_group': 'shared.repo',
                'name': 'shared-b',
                'baseurl': 'http://mirror.example.com/b/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-b',
            },
        }}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'centos',
                'base_package_type': 'rpm',
                'repos_yaml': fname,
            }
            result = methods.handle_repos(
                template_vars, ['shared-a', 'shared-b'], 'enable')
            self.assertEqual(
                1,
                result.count(
                    'cp /etc/yum.repos.d/shared.repo'
                    ' /tmp/kolla-repos-backup/shared.repo'))
            self.assertNotIn('shared-a.repo /tmp/kolla-repos-backup',
                             result)
            self.assertNotIn('shared-b.repo /tmp/kolla-repos-backup',
                             result)
            # each repo still gets its own override file written
            self.assertIn('>/etc/yum.repos.d/shared-a.repo', result)
            self.assertIn('>/etc/yum.repos.d/shared-b.repo', result)
        finally:
            os.unlink(fname)

    def test_get_cleanup_commands_rpm_shared_file_group(self):
        """The shared file is restored once, each own override always."""
        repos = {'rpm': {
            'shared-a': {
                'build_only': True,
                'file_group': 'shared.repo',
                'name': 'shared-a',
                'baseurl': 'http://mirror.example.com/a/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-a',
            },
            'shared-b': {
                'build_only': True,
                'file_group': 'shared.repo',
                'name': 'shared-b',
                'baseurl': 'http://mirror.example.com/b/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-b',
            },
        }}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            result = methods.get_cleanup_commands(
                fname, 'rpm', 'centos', 'x86_64')
            self.assertEqual(
                1,
                result.count(
                    'mv /tmp/kolla-repos-backup/shared.repo'
                    ' /etc/yum.repos.d/shared.repo'))
            self.assertIn('rm -f /etc/yum.repos.d/shared-a.repo', result)
            self.assertIn('rm -f /etc/yum.repos.d/shared-b.repo', result)
        finally:
            os.unlink(fname)

    def _rocky_mirror_override(self):
        """The exact override shape documented for Rocky, minus file_group.

        repos_yaml overrides replace a repo's whole entry, so this matches
        what a real user would write per doc/source/admin/image-building
        .rst - it must not restate 'file_group' for the fix to be tested.
        """
        return {'rocky': {
            'baseos': {
                'build_only': True,
                'name': 'baseos',
                'baseurl': 'http://mirror.example.com/rocky/10/BaseOS/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
            },
            'appstream': {
                'build_only': True,
                'name': 'appstream',
                'baseurl': 'http://mirror.example.com/rocky/10/AppStream/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
            },
            'crb': {
                'build_only': True,
                'name': 'crb',
                'baseurl': 'http://mirror.example.com/rocky/10/CRB/',
                'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
            },
        }}

    def test_handle_repos_rocky_baseos_backs_up_shared_file(self):
        """file_group must be resolved even if the override omits it.

        Rocky's baseos/appstream/crb live in rocky.repo, not their own
        .repo files, and a repos_yaml override doesn't restate file_group.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(self._rocky_mirror_override(), f)
            fname = f.name
        try:
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'rocky',
                'base_package_type': 'rpm',
                'repos_yaml': fname,
            }
            result = methods.handle_repos(
                template_vars, ['baseos', 'appstream'], 'enable')
            self.assertEqual(
                1,
                result.count(
                    'cp /etc/yum.repos.d/rocky.repo'
                    ' /tmp/kolla-repos-backup/rocky.repo'))
            self.assertNotIn('baseos.repo /tmp/kolla-repos-backup', result)
            self.assertNotIn('appstream.repo /tmp/kolla-repos-backup',
                             result)
        finally:
            os.unlink(fname)

    def test_get_cleanup_commands_rocky_restores_shared_file(self):
        """Restoring baseos/appstream/crb recovers the shared rocky.repo."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(self._rocky_mirror_override(), f)
            fname = f.name
        try:
            result = methods.get_cleanup_commands(
                fname, 'rpm', 'rocky', 'x86_64')
            self.assertEqual(
                1,
                result.count(
                    'mv /tmp/kolla-repos-backup/rocky.repo'
                    ' /etc/yum.repos.d/rocky.repo'))
            self.assertIn('rm -f /etc/yum.repos.d/baseos.repo', result)
            self.assertIn('rm -f /etc/yum.repos.d/appstream.repo', result)
            self.assertIn('rm -f /etc/yum.repos.d/crb.repo', result)
        finally:
            os.unlink(fname)

    def test_handle_repos_build_only_no_double_backup(self):
        """Each distinct file is backed up exactly once per handle_repos."""
        repos = {'debian': {
            'mirror-a': {
                'build_only': True,
                'url': 'http://mirror.example.com/a',
                'suite': 'trixie',
                'component': 'main',
                'gpg_key': '/usr/share/keyrings/debian-archive-keyring.gpg',
            },
            'mirror-b': {
                'build_only': True,
                'url': 'http://mirror.example.com/b',
                'suite': 'trixie',
                'component': 'main',
                'gpg_key': '/usr/share/keyrings/debian-archive-keyring.gpg',
            },
        }}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'debian',
                'base_package_type': 'deb',
                'openstack_release_codename': 'Gazpacho',
                'repos_yaml': fname,
            }
            result = methods.handle_repos(
                template_vars, ['mirror-a', 'mirror-b'], 'enable')
            self.assertEqual(
                1,
                result.count(
                    'cp /etc/apt/sources.list.d/mirror-a.sources'
                    ' /tmp/kolla-repos-backup/mirror-a.sources'))
            self.assertEqual(
                1,
                result.count(
                    'cp /etc/apt/sources.list.d/mirror-b.sources'
                    ' /tmp/kolla-repos-backup/mirror-b.sources'))
        finally:
            os.unlink(fname)

    def test_handle_repos_without_build_only_no_backup(self):
        template_vars = {
            'base_arch': 'x86_64',
            'base_distro': 'debian',
            'base_package_type': 'deb',
            'openstack_release_codename': 'Gazpacho',
        }
        result = methods.handle_repos(template_vars, ['grafana'], 'enable')
        self.assertNotIn('kolla-repos-backup', result)

    def test_get_cleanup_commands_deb(self):
        repos = {'debian': {'build-only-mirror': {
            'build_only': True,
            'url': 'http://mirror.example.com/debian',
            'suite': 'trixie',
            'component': 'main',
            'gpg_key': '/usr/share/keyrings/debian-archive-keyring.gpg',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            result = methods.get_cleanup_commands(
                fname, 'deb', 'debian', 'x86_64')
            self.assertTrue(result.startswith('RUN '))
            self.assertIn(
                '[ -f /tmp/kolla-repos-backup/build-only-mirror.enabled ]',
                result)
            self.assertIn(
                'mv /tmp/kolla-repos-backup/build-only-mirror.sources'
                ' /etc/apt/sources.list.d/build-only-mirror.sources',
                result)
            self.assertIn(
                'rm -f /etc/apt/sources.list.d/build-only-mirror.sources',
                result)
            self.assertIn('rm -rf /tmp/kolla-repos-backup', result)
        finally:
            os.unlink(fname)

    def test_get_cleanup_commands_rpm(self):
        repos = {'rpm': {'build-only-mirror': {
            'build_only': True,
            'name': 'build-only-mirror',
            'baseurl': 'http://mirror.example.com/',
            'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            result = methods.get_cleanup_commands(
                fname, 'rpm', 'centos', 'x86_64')
            self.assertTrue(result.startswith('RUN '))
            self.assertIn(
                '[ -f /tmp/kolla-repos-backup/build-only-mirror.repo'
                '.enabled ]',
                result)
            self.assertIn(
                'mv /tmp/kolla-repos-backup/build-only-mirror.repo'
                ' /etc/yum.repos.d/build-only-mirror.repo',
                result)
            self.assertIn(
                'rm -f /etc/yum.repos.d/build-only-mirror.repo',
                result)
            self.assertIn('rm -rf /tmp/kolla-repos-backup', result)
        finally:
            os.unlink(fname)

    def test_get_cleanup_commands_empty_without_build_only(self):
        result = methods.get_cleanup_commands(None, 'deb', 'debian', 'x86_64')
        self.assertEqual('', result)

    def test_get_cleanup_commands_skips_distro_repos(self):
        """distro: True repos are a no-op in handle_repos."""
        repos = {'debian': {'debian': {
            'build_only': True,
            'distro': True,
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                         delete=False) as f:
            yaml.dump(repos, f)
            fname = f.name
        try:
            result = methods.get_cleanup_commands(
                fname, 'deb', 'debian', 'x86_64')
            self.assertEqual('', result)
        finally:
            os.unlink(fname)

    def test_repos_yaml_rpm_section_override_not_blocked_by_distro_section(
            self):
        """Overriding distro repos in 'rpm' section must not be undone.

        The more-specific distro section must not merge distro:True back
        on top of a URL-bearing override from the generic 'rpm' section.
        """
        base = 'http://mirror.example.com/centos/10'
        gpgkey = 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial'
        repos = {'rpm': {
            'baseos': {
                'name': 'baseos',
                'baseurl': base + '/BaseOS/$basearch/',
                'gpgkey': gpgkey,
            },
            'appstream': {
                'name': 'appstream',
                'baseurl': base + '/AppStream/$basearch/',
                'gpgkey': gpgkey,
            },
            'crb': {
                'name': 'crb',
                'baseurl': base + '/CRB/$basearch/',
                'gpgkey': gpgkey,
            },
        }}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'centos',
                'base_package_type': 'rpm',
                'repos_yaml': f.name,
            }
            result = methods.handle_repos(
                template_vars, ['baseos', 'appstream', 'crb'], 'enable')
            self.assertIn('mirror.example.com', result)

    def test_enable_repos_openstack_release_codename_substitution(self):
        repos = {'ubuntu': {'ubuntu-cloud-archive': {
            'url': 'http://ubuntu-cloud.archive.canonical.com/ubuntu',
            'suite': 'noble-updates/{openstack_release_codename}',
            'component': 'main',
            'gpg_key': '/usr/share/keyrings/ubuntu-cloud-keyring.gpg',
        }}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.dump(repos, f)
            f.flush()
            template_vars = {
                'base_arch': 'x86_64',
                'base_distro': 'ubuntu',
                'base_package_type': 'deb',
                'openstack_release_codename': 'Gazpacho',
                'repos_yaml': f.name,
            }
            result = methods.handle_repos(
                template_vars, ['ubuntu-cloud-archive'], 'enable')
            self.assertIn('noble-updates/gazpacho', result)
