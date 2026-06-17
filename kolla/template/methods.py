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
echo 'Signed-By: {signed_by}' \
>>/etc/apt/sources.list.d/{repo}.sources"
APT_TRUSTED = " && echo 'Trusted: yes' \
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
DNF_REMOVE_EXISTING = \
    "grep -rlF '[{name}]' /etc/yum.repos.d/ 2>/dev/null | xargs -r rm -f"
DNF_REPO = "echo '[{name}]' >/etc/yum.repos.d/{repo}.repo && \
echo 'name={name}' >>/etc/yum.repos.d/{repo}.repo && \
echo 'enabled=1' >>/etc/yum.repos.d/{repo}.repo"
DNF_REPO_GPGCHECK = " && echo 'repo_gpgcheck={repo_gpgcheck}' \
>>/etc/yum.repos.d/{repo}.repo"

BACKUP_DIR = '/tmp/kolla-repos-backup'  # nosec B108
APT_BACKUP = (
    'mkdir -p {backup_dir}'
    ' && cp /etc/apt/sources.list.d/{repo}.sources'
    ' {backup_dir}/{repo}.sources 2>/dev/null || true'
    ' && touch {backup_dir}/{repo}.enabled'
    ' && '
)
RPM_BACKUP = (
    'mkdir -p {backup_dir}'
    ' && cp /etc/yum.repos.d/{file}'
    ' {backup_dir}/{file} 2>/dev/null || true'
    ' && touch {backup_dir}/{file}.enabled'
    ' && '
)


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


def _load_repos(repos_yaml_override=None):
    """Load default repos.yaml and merge an optional override file."""
    default_repofile = os.path.dirname(
        os.path.realpath(__file__)) + '/repos.yaml'
    with open(default_repofile, 'r') as f:
        repo_data = yaml.safe_load(f)

    if repos_yaml_override:
        with open(repos_yaml_override, 'r') as f:
            for section, repos in yaml.safe_load(f).items():
                if section in repo_data:
                    repo_data[section].update(repos)
                else:
                    repo_data[section] = repos

    return repo_data


def _build_repo_list(repo_data, base_package_type, base_distro, base_arch):
    """Flatten repo_data sections for the current distro/arch into one dict."""
    result = {}
    for section in (base_package_type, base_distro,
                    '%s-%s' % (base_distro, base_arch)):
        for repo_name, repo_info in repo_data.get(section, {}).items():
            if repo_name in result:
                merged = {**result[repo_name], **repo_info}
                if any(k in merged for k in
                       ('baseurl', 'metalink', 'mirrorlist', 'url')):
                    merged.pop('distro', None)
                result[repo_name] = merged
            else:
                result[repo_name] = repo_info
    return result


@pass_context
def handle_repos(context, reponames, mode):
    """Generate Dockerfile RUN commands to enable or disable package repos.

    Takes a list of logical repo names (e.g. 'ceph', 'grafana') and a mode
    ('enable' or 'disable'), looks them up in repos.yaml (merging any
    user-supplied repos_yaml override), and returns a shell command string
    suitable for use in a Dockerfile RUN instruction.

    Repo names are distro/arch-agnostic aliases that map to the real repo
    name and URL for the target platform.  So 'ceph' becomes
    'centos-ceph-squid' on CentOS, uses UCA on Ubuntu, and so on.
    Distro/arch sections are not required to have all entries - missing ones
    are silently ignored.

    NOTE(hrw): we need to handle CentOS, Debian and Ubuntu with one macro.
    """

    if not isinstance(reponames, list):
        raise TypeError("First argument should be a list of repositories")

    repos_yaml = context.get('repos_yaml')
    repo_data = _load_repos(repos_yaml)
    default_repo_data = _load_repos()

    base_package_type = context.get('base_package_type')
    base_distro = context.get('base_distro')
    base_arch = context.get('base_arch')
    image_name = context.get('image_name')
    openstack_release_codename = context.get('openstack_release_codename')

    commands = ''
    backed_up_files = set()

    try:
        repo_list = _build_repo_list(
            repo_data, base_package_type, base_distro, base_arch)
    except KeyError:
        # NOTE(hrw): Fallback to distro list
        repo_list = repo_data[base_distro]

    # NOTE: repos_yaml overrides replace a repo's whole entry (see
    # _load_repos), so an override that doesn't restate 'file_group' would
    # otherwise lose it. Keep the default list around to fall back to the
    # distro's real on-disk layout for repos sharing a file.
    default_repo_list = _build_repo_list(
        default_repo_data, base_package_type, base_distro, base_arch)

    if base_package_type == 'rpm' and repos_yaml:
        distro_overridden = {r for r, d in repo_list.items()
                             if not d.get('distro')
                             and default_repo_list.get(r, {}).get('distro')}
        if distro_overridden:
            overridden_groups = {
                default_repo_list[r].get('file_group')
                for r in distro_overridden
                if default_repo_list.get(r, {}).get('file_group')}
            distro_not_overridden = sorted(
                r for r, d in repo_list.items()
                if d.get('distro')
                and r not in distro_overridden
                and d.get('file_group') in overridden_groups)
            if distro_not_overridden:
                raise ValueError(
                    "Repositories %s override distro-provided repos and will "
                    "remove their .repo file. Repositories %s are still using "
                    "distro defaults and share the same file. Please also "
                    "override them in your repos.yaml."
                    % (sorted(distro_overridden), distro_not_overridden))

    for index, repo in enumerate(reponames):
        try:
            _repo = repo_list[repo]
            if base_package_type == 'rpm':
                if mode == 'enable':
                    if not _repo.get('distro'):
                        if _repo.get('build_only'):
                            # NOTE: some distros (e.g. Rocky's baseos,
                            # appstream and crb) share a single .repo file,
                            # so back up that shared file, not one named
                            # after this repo, or the original content is
                            # lost once handle_repos rewrites the file.
                            repo_file = (
                                _repo.get('file_group')
                                or default_repo_list.get(repo, {}).get(
                                    'file_group')
                                or '{}.repo'.format(repo))
                            if repo_file not in backed_up_files:
                                commands += RPM_BACKUP.format(
                                    backup_dir=BACKUP_DIR, file=repo_file)
                                backed_up_files.add(repo_file)
                        commands += DNF_REMOVE_EXISTING.format(
                            name=_repo['name'])
                        commands += " && "
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

                        if not any(k in _repo for k in
                                   ('baseurl', 'metalink', 'mirrorlist')):
                            raise ValueError(
                                "Repository '%s' has no baseurl, metalink,"
                                " or mirrorlist" % repo)
                        if 'gpgkey' not in _repo:
                            raise ValueError(
                                "Repository '%s' has no gpgkey" % repo)
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
                    else:
                        commands += DNF_ENABLE.format(name=_repo['name'])

                    if index != len(reponames) - 1:
                        commands += " && "

                elif mode == 'disable' and _repo.get('distro'):
                    commands += DNF_DISABLE.format(name=_repo['name'])

            elif base_package_type == "deb":
                if mode == "enable" and not _repo.get('distro'):
                    if _repo.get('build_only'):
                        sources_file = (
                            '/etc/apt/sources.list.d/{}.sources'.format(repo))
                        if sources_file not in backed_up_files:
                            commands += APT_BACKUP.format(
                                backup_dir=BACKUP_DIR, repo=repo)
                            backed_up_files.add(sources_file)
                    gpg_key = _repo['gpg_key']
                    signed_by = gpg_key if gpg_key.startswith('/') \
                        else '/etc/kolla/apt-keys/' + gpg_key
                    suite = _repo['suite'].replace(
                      '{openstack_release_codename}',
                      openstack_release_codename.lower())
                    commands += APT_REPO.format(
                        component=_repo['component'],
                        signed_by=signed_by,
                        suite=suite,
                        url=_repo['url'],
                        repo=repo,
                    )
                    if _repo.get('trusted'):
                        commands += APT_TRUSTED.format(repo=repo)

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


def get_cleanup_commands(repos_yaml, base_package_type, base_distro,
                         base_arch):
    """Return a RUN command string restoring or removing build_only repos.

    Repos marked build_only: true are backed up before being overwritten in
    handle_repos(). This function generates the matching restore commands so
    that mirror URLs are not baked into the final image. Repos that had no
    prior file (no backup exists) are deleted instead of restored.

    Returns an empty string when there are no build_only repos.
    """
    repo_data = _load_repos(repos_yaml)
    repo_list = _build_repo_list(
        repo_data, base_package_type, base_distro, base_arch)
    default_repo_list = _build_repo_list(
        _load_repos(), base_package_type, base_distro, base_arch)

    cleanup_cmds = []
    restored_file_groups = set()
    for repo_name, repo_info in repo_list.items():
        if not repo_info.get('build_only'):
            continue
        if base_package_type == 'rpm' and not repo_info.get('distro'):
            own_file = '{}.repo'.format(repo_name)
            file_group = (
                repo_info.get('file_group')
                or default_repo_list.get(repo_name, {}).get('file_group')
                or own_file)
            if file_group != own_file:
                # handle_repos always writes this repo's override to
                # own_file, regardless of where the original repo lived,
                # so it always needs dropping on its own.
                cleanup_cmds.append(
                    'rm -f /etc/yum.repos.d/{}'.format(own_file))
                if file_group in restored_file_groups:
                    continue
                restored_file_groups.add(file_group)
            cleanup_cmds.append(
                '[ -f {backup_dir}/{file}.enabled ]'
                ' && ( mv {backup_dir}/{file}'
                ' /etc/yum.repos.d/{file} 2>/dev/null'
                ' || rm -f /etc/yum.repos.d/{file} )'
                ' || true'.format(
                    backup_dir=BACKUP_DIR, file=file_group))
        elif base_package_type == 'deb' and not repo_info.get('distro'):
            cleanup_cmds.append(
                '[ -f {backup_dir}/{repo}.enabled ]'
                ' && ( mv {backup_dir}/{repo}.sources'
                ' /etc/apt/sources.list.d/{repo}.sources 2>/dev/null'
                ' || rm -f /etc/apt/sources.list.d/{repo}.sources )'
                ' || true'.format(
                    backup_dir=BACKUP_DIR, repo=repo_name))

    if not cleanup_cmds:
        return ''

    cleanup_cmds.append('rm -rf {}'.format(BACKUP_DIR))
    return 'RUN ' + ' \\\n    && '.join(cleanup_cmds)


@pass_context
def cleanup_repos(context):
    """Jinja2-callable wrapper around get_cleanup_commands()."""
    return get_cleanup_commands(
        context.get('repos_yaml'),
        context.get('base_package_type'),
        context.get('base_distro'),
        context.get('base_arch'),
    )


def raise_error(msg: str) -> t.NoReturn:
    raise Exception(msg)
