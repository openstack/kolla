#!/usr/bin/env python

# Copyright 2015 Sam Yaple
#
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

# This file exists because we want to create and delete any network
# namespaces from the host mount namespace. This allows the host to
# access all of the neutron network namespaces as well as all
# containers that bind mount /run/netns from the host.

# This is required for "thin" neutron containers to function properly. However,
# due to a missing feature/bug in Docker it is not possible to use this script
# at this time. Once Docker updates with this feature we will usre this again.

import nsenter
import subprocess  # nosec
import sys


def host_mnt_exec(cmd):
    try:
        with nsenter.ExitStack() as stack:
            stack.enter_context(
                nsenter.Namespace(
                    '1',
                    'mnt',
                    proc='/var/lib/kolla/host_proc/'))
            process_ = subprocess.Popen(cmd)  # nosec

    except Exception as e:
        print(
            "An error has occurred with a component that Kolla manages."
            " Please file a bug")
        print("Error: ", e)

    return process_


if len(sys.argv) > 2:
    # We catch all commands that ip will accept that refer
    # to creating or deleteing a Network namespace
    if str(sys.argv[1]).startswith("net") and (
            str(sys.argv[2]).startswith("a") or
            str(sys.argv[2]).startswith("d")):
        # This cmd is executed in the host mount namespace
        cmd = ["/usr/bin/env", "ip"] + sys.argv[1:]
        sys.exit(host_mnt_exec(cmd).returncode)
    else:
        cmd = ["/var/lib/kolla/ip"] + sys.argv[1:]
else:
    cmd = ["/var/lib/kolla/ip"]

    if len(sys.argv) == 2:
        cmd = cmd + sys.argv[1:]

process_ = subprocess.Popen(cmd)  # nosec
sys.exit(process_.returncode)
