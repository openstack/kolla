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
import yaml

from jinja2 import pass_context


def debian_package_install(packages, clean_package_cache=True):
    """Jinja utility method for building debian-based package install command.

    apt-get is not capable of installing .deb files from a URL and the
    template logic to construct a series of steps to install regular packages
    from apt repos as well as .deb files that need to be downloaded, manually
    installed, and cleaned up is complicated. This method will construct the
    proper string required to install all packages in a way that's a bit
    easier to follow.

    :param packages: a list of strings that are either packages to install
    from an apt repo, or URLs to .deb files
    :type packages: list

    :returns: string suitable to provide to RUN command in a Dockerfile that
    will install the given packages
    :rtype: string
    """
    cmds = []

    # divide the list into two groups, one for regular packages and one for
    # URL packages
    reg_packages, url_packages = [], []
    for package in packages:
        if package.startswith('http'):
            url_packages.append(package)
        else:
            reg_packages.append(package)

    # handle the apt-get install
    if reg_packages:
        cmds.append('apt-get --error-on=any update')
        cmds.append('apt-get -y install --no-install-recommends {}'.format(
            ' '.join(reg_packages)
        ))
        if clean_package_cache:
            cmds.append('apt-get clean')
            cmds.append('rm -rf /var/lib/apt/lists/*')

    # handle URL packages
    for url in url_packages:
        # the path portion should be the file name
        name = url[url.rfind('/') + 1:]
        cmds.extend([
            'curl --location {} -o {}'.format(url, name),
            'dpkg -i {}'.format(name),
            'rm -rf {}'.format(name),
        ])

    # return the list of commands
    return ' && '.join(cmds)


@pass_context
def handle_repos(context, reponames, mode):
    """NOTE(hrw): we need to handle CentOS, Debian and Ubuntu with one macro.

    Repo names have to be simple names mapped to proper ones.  So 'ceph' ==
    'centos-ceph-pacific' for CentOS, UCA for Ubuntu (enabled by default) and
    something else for Debian.
    Distro/arch are not required to have all entries - we ignore missing ones.
    """

    if mode == 'enable':
        rpm_switch = '--enable'
    elif mode == 'disable':
        rpm_switch = '--disable'
    else:
        raise KeyError

    if not isinstance(reponames, list):
        raise TypeError("First argument should be a list of repositories")

    if context.get('repos_yaml'):
        repofile = context.get('repos_yaml')
    else:
        repofile = os.path.dirname(os.path.realpath(__file__)) + '/repos.yaml'

    with open(repofile, 'r') as repos_file:
        repo_data = {}
        for name, params in yaml.safe_load(repos_file).items():
            repo_data[name] = params

    base_package_type = context.get('base_package_type')
    base_distro = context.get('base_distro')
    base_arch = context.get('base_arch')

    commands = ''

    try:
        repo_list = repo_data['%s-%s' % (base_distro, base_arch)]
    except KeyError:
        # NOTE(hrw): Fallback to distro list
        repo_list = repo_data[base_distro]

    for repo in reponames:
        try:
            if base_package_type == 'rpm':
                commands += ' %s %s' % (rpm_switch, repo_list[repo])
            elif base_package_type == 'deb':
                if mode == 'enable':
                    commands += f"""echo 'Uris: {repo_list[repo]['url']}' \
>/etc/apt/sources.list.d/{repo}.sources \
&& echo 'Components: {repo_list[repo]['component']}' \
>>/etc/apt/sources.list.d/{repo}.sources \
&& echo 'Types: deb' >>/etc/apt/sources.list.d/{repo}.sources \
&& echo 'Suites: {repo_list[repo]['suite']}' \
>>/etc/apt/sources.list.d/{repo}.sources \
&& echo 'Signed-By: /etc/kolla/apt-keys/{repo_list[repo]['gpg_key']}' \
>>/etc/apt/sources.list.d/{repo}.sources \
&& """
                    if repo_list[repo]['arch']:
                        commands += f"""echo 'Architectures: {repo_list[repo]['arch']}' \
>>/etc/apt/sources.list.d/{repo}.sources \
&& """
        except KeyError:
            # NOTE(hrw): we ignore missing repositories for a given
            # distro/arch
            pass

    if base_package_type == 'rpm' and commands:
        # NOTE(hrw): if commands is empty then no repos are enabled
        # otherwise we need to add command to handle repositories
        # NOTE(hrw) dnf errors out if we enable unknown repo
        commands = 'dnf config-manager %s || true' % commands
    elif base_package_type == 'deb':
        # NOTE(hrw): Debian commands end with '&&'
        commands = commands[0:-4]

    if commands:
        commands = "RUN %s" % commands

    return commands
