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
        "bifrost-base",      # someone need to get upstream working first
        "monasca-base",      # 'confluent-kafka' requires newer libfdkafka-dev
                             # than distributions have (v1.9.0+ in Zed)
        "prometheus-msteams",  # no aarch64 binary
        "prometheus-mtail",  # no aarch64 binary
        "skydive-base",      # no aarch64 binary
    },

    # Issues for SHA1 keys:
    # https://github.com/elastic/elasticsearch/issues/85876
    # https://github.com/grafana/grafana/issues/41036
    # Issue with telegraf:
    # https://github.com/influxdata/telegraf/issues/12303
    'centos': {
        "elasticsearch",         # SHA1 gpg key
        "hacluster-pcs",         # Missing crmsh package
        "kibana",                # SHA1 gpg key
        "logstash",              # SHA1 gpg key
        "nova-spicehtml5proxy",  # Missing spicehtml5 package
        "ovsdpdk",               # Not supported on CentOS
        "tgtd",                  # Not supported on CentOS
        "telegraf",              # Package is not signed
    },

    'debian': {
    },

    'rocky': {
        "elasticsearch",         # SHA1 gpg key
        "hacluster-pcs",         # Missing crmsh package
        "kibana",                # SHA1 gpg key
        "logstash",              # SHA1 gpg key
        "nova-spicehtml5proxy",  # Missing spicehtml5 package
        "ovsdpdk",               # Not supported on CentOS
        "tgtd",                  # Not supported on CentOS
        "telegraf",              # Package is not signed
    },

    'ubuntu': {
        "collectd",              # Missing collectd-core package
        "telegraf",              # Missing collectd-core package
    },

    'ubuntu+aarch64': {
        "barbican-base",  # https://github.com/unbit/uwsgi/issues/2434
        "kibana",         # no binary package
    },

    'centos+aarch64': {
        "kibana",         # no binary package
        "telegraf",       # no binary package
    },
}
