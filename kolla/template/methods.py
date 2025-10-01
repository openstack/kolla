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

from kolla.image.utils import LOG
import os
import typing as t

import yaml

from jinja2 import pass_context

APT_ARCH = " && echo 'Architectures: {arch}' \
>>/etc/apt/sources.list.d/{repo}.sources"
APT_REPO = "echo 'Uris: {url}' >/etc/apt/sources.list.d/{repo}.sources && \
echo 'Components: {component}' >>/etc/apt/sources.list.d/{repo}.sources && \
echo 'Types: deb' >>/etc/apt/sources.list.d/{repo}.sources && \
echo 'Suites: {suite}' >>/etc/apt/sources.list.d/{repo}.sources && \
echo 'Signed-By: /etc/kolla/apt-keys/{gpg_key}' \
>>/etc/apt/sources.list.d/{repo}.sources"
DNF_BASEURL = " && echo 'baseurl={baseurl}' >>/etc/yum.repos.d/{repo}.repo"
DNF_DISABLE = "dnf config-manager --disable {name} || true"
DNF_ENABLE = "dnf config-manager --enable {name} || true"
DNF_GPGCHECK = " && echo 'gpgcheck={gpgcheck}' >>/etc/yum.repos.d/{repo}.repo"
DNF_GPGKEY = " && echo 'gpgkey={gpgkey}' >>/etc/yum.repos.d/{repo}.repo"
DNF_GPGKEY_ADD = " && echo '       {gpgkey}' >>/etc/yum.repos.d/{repo}.repo"
DNF_METALINK = " && echo 'metalink={metalink}' >>/etc/yum.repos.d/{repo}.repo"
DNF_MIRRORLIST = " && \
echo 'mirrorlist={mirrorlist}' >>/etc/yum.repos.d/{repo}.repo"
DNF_REPO = "echo '[{name}]' >/etc/yum.repos.d/{repo}.repo && \
echo 'name={name}' >>/etc/yum.repos.d/{repo}.repo && \
echo 'enabled=1' >>/etc/yum.repos.d/{repo}.repo"
DNF_REPO_GPGCHECK = " && echo 'repo_gpgcheck={repo_gpgcheck}' \
>>/etc/yum.repos.d/{repo}.repo"


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
    image_name = context.get('image_name')

    commands = ''

    try:
        repo_list = repo_data[base_distro] | \
                    repo_data['%s-%s' % (base_distro, base_arch)]
    except KeyError:
        # NOTE(hrw): Fallback to distro list
        repo_list = repo_data[base_distro]

    for index, repo in enumerate(reponames):
        try:
            _repo = repo_list[repo]
            if base_package_type == 'rpm':
                if mode == 'enable':
                    if not _repo.get('distro'):
                        commands += DNF_REPO.format(
                            name=_repo['name'],
                            repo=repo,
                        )
                        if _repo.get('gpgcheck'):
                            commands += DNF_GPGCHECK.format(
                                            gpgcheck=_repo['gpgcheck'],
                                            repo=repo)

                        if _repo.get('repo_gpgcheck'):
                            commands += DNF_REPO_GPGCHECK.format(
                                        repo_gpgcheck=_repo['repo_gpgcheck'],
                                        repo=repo)

                        # NOTE(mnasiadka): Support multiple gpgkeys
                        gpgkeys = _repo['gpgkey'].splitlines()
                        for _, gpgkey in enumerate(gpgkeys):
                            if _ == 0:
                                commands += DNF_GPGKEY.format(gpgkey=gpgkey,
                                                              repo=repo)
                            else:
                                commands += DNF_GPGKEY_ADD.format(
                                    gpgkey=gpgkey,
                                    repo=repo)
                    else:
                        commands += DNF_ENABLE.format(name=_repo['name'])

                    if 'baseurl' in _repo:
                        # NOTE(mnasiadka): Support multiple baseurls
                        baseurl = _repo['baseurl'].splitlines()
                        for url in baseurl:
                            commands += DNF_BASEURL.format(baseurl=url,
                                                           repo=repo)
                    elif 'metalink' in _repo:
                        commands += DNF_METALINK.format(
                            metalink=_repo['metalink'], repo=repo
                        )

                    elif 'mirrorlist' in _repo:
                        commands += DNF_MIRRORLIST.format(
                            mirrorlist=_repo['mirrorlist'], repo=repo
                        )

                    if index != len(reponames) - 1:
                        commands += " && "

                elif mode == 'disable' and _repo.get('distro'):
                    commands += DNF_DISABLE.format(name=_repo['name'])

            elif base_package_type == "deb":
                if mode == "enable":
                    commands += APT_REPO.format(
                        component=_repo['component'],
                        gpg_key=_repo['gpg_key'],
                        suite=_repo['suite'],
                        url=_repo['url'],
                        repo=repo,
                    )

                    if 'arch' in _repo:
                        commands += APT_ARCH.format(
                            arch=_repo['arch'], repo=repo
                        )

                    if index != len(reponames) - 1:
                        commands += ' && '
        except KeyError as e:
            LOG.exception("Error enabling repository %s in image %s", e,
                          image_name)
            raise

    if commands:
        commands = "RUN %s" % commands

    return commands


def raise_error(msg: str) -> t.NoReturn:
    raise Exception(msg)
