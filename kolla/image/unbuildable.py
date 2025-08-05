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

# The dictionary of unbuildable images supports keys in the format:
# '<distro>+<arch>' where each component is optional and can be omitted along
# with the + separator which means that component is irrelevant. Otherwise all
# must match for skip to happen.
UNBUILDABLE_IMAGES = {
    'aarch64': {
        "bifrost-base",        # someone need to get upstream working first
    },

    # Issues for SHA1 keys:
    # https://github.com/grafana/grafana/issues/41036
    'centos': {
        "collectd",              # CS10 no opstools repo
        "hacluster-pcs",         # Missing crmsh package
        "nova-spicehtml5proxy",  # Missing spicehtml5 package
        "ovsdpdk",               # Not supported on CentOS
        "redis-base",            # Missing in CS10
        "telegraf",              # CS10 no opstools repo
        "tgtd",                  # Not supported on CentOS
    },

    'debian': {
        "openvswitch-netcontrold",
        # https://bugs.launchpad.net/kolla/+bug/2027668
    },

    'rocky': {
        "collectd",              # Missing libpqos.so.4()(64bit)
        "hacluster-pcs",         # Missing crmsh package
        "nova-spicehtml5proxy",  # Missing spicehtml5 package
        "ovsdpdk",               # Not supported on CentOS
        "redis-base",            # Missing in Rocky10
        "telegraf",              # CS10 no opstools repo
        "tgtd",                  # Not supported on CentOS
    },

    'ubuntu': {
    },

    'ubuntu+aarch64': {
    },

    'centos+aarch64': {
    },
}
