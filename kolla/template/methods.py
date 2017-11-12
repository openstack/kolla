#!/usr/bin/env python

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


def debian_package_install(packages):
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
        cmds.append('apt-get update')
        cmds.append('apt-get -y install --no-install-recommends {}'.format(
            ' '.join(reg_packages)
        ))
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
