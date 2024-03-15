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

SOURCES = {
    'openstack-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/requirements/'
                     'requirements-${openstack_branch}.tar.gz')},
    'openstack-base-plugin-pycadf': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/pycadf/'
                     'pycadf-3.1.1.tar.gz')},
    'aodh-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/aodh/'
                     'aodh-${openstack_branch}.tar.gz')},
    'barbican-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/barbican/'
                     'barbican-${openstack_branch}.tar.gz')},
    'bifrost-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/bifrost/'
                     'bifrost-${openstack_branch}.tar.gz')},
    'blazar-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar/'
                     'blazar-${openstack_branch}.tar.gz')},
    'ceilometer-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ceilometer/'
                     'ceilometer-${openstack_branch}.tar.gz')},
    'cinder-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cinder/'
                     'cinder-${openstack_branch}.tar.gz')},
    'cloudkitty-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cloudkitty/'
                     'cloudkitty-${openstack_branch}.tar.gz')},
    'cyborg-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cyborg/'
                     'cyborg-${openstack_branch}.tar.gz')},
    'designate-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/designate/'
                     'designate-${openstack_branch}.tar.gz')},
    'etcd': {
    # NOTE(wszumski): It is suggested to upgrade one minor version at a time:
    # https://github.com/etcd-io/website/blob/cf046546dec9e1dcea966dc21ea38027c3290e9a/content/en/docs/v3.4/upgrades/upgrade_3_4.md#upgrade-requirements
        'version': '3.4.27',
        'type': 'url',
        'sha256': {
            'amd64': 'a32d21e006252dbc3405b0645ba8468021ed41376974b573285927bf39b39eb9',  # noqa: E501
            'arm64': 'ed7e257c225b9b9545fac22246b97f4074a4b5109676e92dbaebfb9315b69cc0'},  # noqa: E501
        'location': ('https://github.com/etcd-io/etcd/'
                     'releases/download/v${version}'
                     '/etcd-v${version}-linux-${debian_arch}.tar.gz')},
    'freezer-api': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/freezer-api/'
                     'freezer-api-${openstack_branch}.tar.gz')},
    'freezer-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/freezer/'
                     'freezer-${openstack_branch}.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/glance/'
                     'glance-${openstack_branch}.tar.gz')},
    'gnocchi-base': {
        'type': 'git',
        'reference': '4.6.1',
        'location': ('https://github.com/gnocchixyz/'
                     'gnocchi.git')},
    'heat-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/heat/'
                     'heat-${openstack_branch}.tar.gz')},
    'horizon': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/horizon/'
                     'horizon-${openstack_branch}.tar.gz')},
    'horizon-plugin-blazar-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar-dashboard/'
                     'blazar-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-cloudkitty-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cloudkitty-dashboard/'
                     'cloudkitty-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-designate-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/designate-dashboard/'
                     'designate-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-freezer-web-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/freezer-web-ui/'
                     'freezer-web-ui-${openstack_branch}.tar.gz')},
    'horizon-plugin-heat-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/heat-dashboard/'
                     'heat-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-ironic-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic-ui/'
                     'ironic-ui-${openstack_branch}.tar.gz')},
    'horizon-plugin-magnum-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum-ui/'
                     'magnum-ui-${openstack_branch}.tar.gz')},
    'horizon-plugin-manila-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/manila-ui/'
                     'manila-ui-${openstack_branch}.tar.gz')},
    'horizon-plugin-masakari-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/masakari-dashboard/'
                     'masakari-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-mistral-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/mistral-dashboard/'
                     'mistral-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-murano-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/murano-dashboard/'
                     'murano-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-neutron-vpnaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas-dashboard/'
                     'neutron-vpnaas-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-octavia-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/octavia-dashboard/'
                     'octavia-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-sahara-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-dashboard/'
                     'sahara-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-senlin-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/senlin-dashboard/'
                     'senlin-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-solum-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/solum-dashboard/'
                     'solum-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-tacker-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tacker-horizon/'
                     'tacker-horizon-${openstack_branch}.tar.gz')},
    'horizon-plugin-trove-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/trove-dashboard/'
                     'trove-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-venus-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/venus-dashboard/'
                     'venus-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-vitrage-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/vitrage-dashboard/'
                     'vitrage-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-watcher-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher-dashboard/'
                     'watcher-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-zun-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zun-ui/'
                     'zun-ui-${openstack_branch}.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic/'
                     'ironic-${openstack_branch}.tar.gz')},
    'ironic-inspector': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic-inspector/'
                     'ironic-inspector-${openstack_branch}.tar.gz')},
    'ironic-conductor-plugin-prometheus-exporter': {
        'type': 'url',
        'location': (
            '$tarballs_base/openstack/ironic-prometheus-exporter/'
            'ironic-prometheus-exporter-${openstack_branch}.tar.gz')},
    'keystone-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/keystone/'
                     'keystone-${openstack_branch}.tar.gz')},
    'kuryr-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/kuryr/'
                     'kuryr-${openstack_branch}.tar.gz')},
    'kuryr-libnetwork': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/kuryr-libnetwork/'
                     'kuryr-libnetwork-${openstack_branch}.tar.gz')},
    'letsencrypt-lego': {
        'version': 'v4.6.0',
        'type': 'url',
        'sha256': {
            'amd64': 'c0c408788cdec96a4697300211c3944a050bb3d62ed3525a5409c136c94e09cb',  # noqa: E501
            'arm64': 'f5cecda8880d04ffc394049852a797ec120aebf0203ab0f1b877a0cd89bb0b3e'},  # noqa: E501
        'location': ('https://github.com/go-acme/lego/'
                     'releases/download/${version}/'
                     'lego_${version}_linux_${debian_arch}.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum/'
                     'magnum-${openstack_branch}.tar.gz')},
    'manila-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/manila/'
                     'manila-${openstack_branch}.tar.gz')},
    'masakari-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/masakari/'
                     'masakari-${openstack_branch}.tar.gz')},
    'masakari-monitors': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/masakari-monitors/'
                     'masakari-monitors-${openstack_branch}.tar.gz')},
    'mistral-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/mistral/'
                     'mistral-${openstack_branch}.tar.gz')},
    'mistral-base-plugin-tacker': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tacker/'
                     'tacker-${openstack_branch}.tar.gz')},
    'murano-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/murano/'
                     'murano-${openstack_branch}.tar.gz')},
    'neutron-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron/'
                     'neutron-${openstack_branch}.tar.gz')},
    'neutron-base-plugin-networking-baremetal': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-baremetal/'
                     'networking-baremetal-${openstack_branch}.tar.gz')},
    'neutron-base-plugin-networking-generic-switch': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-generic-switch/'
                     'networking-generic-switch-${openstack_branch}.tar.gz')},
    'neutron-base-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-sfc/'
                     'networking-sfc-${openstack_branch}.tar.gz')},
    'neutron-base-plugin-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas/'
                     'neutron-vpnaas-${openstack_branch}.tar.gz')},
    'neutron-bgp-dragent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-dynamic-routing/'
                     'neutron-dynamic-routing-${openstack_branch}.tar.gz')},
    'neutron-server-plugin-neutron-dynamic-routing': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-dynamic-routing/'
                     'neutron-dynamic-routing-${openstack_branch}.tar.gz')},
    'neutron-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas/'
                     'neutron-vpnaas-${openstack_branch}.tar.gz')},
    'nova-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/nova/'
                     'nova-${openstack_branch}.tar.gz')},
    'nova-base-plugin-blazar': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar-nova/'
                     'blazar-nova-${openstack_branch}.tar.gz')},
    'octavia-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/octavia/'
                     'octavia-${openstack_branch}.tar.gz')},
    'octavia-api-plugin-ovn-octavia-provider': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ovn-octavia-provider/'
                     'ovn-octavia-provider-${openstack_branch}.tar.gz')},
    'octavia-driver-agent-plugin-ovn-octavia-provider': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ovn-octavia-provider/'
                     'ovn-octavia-provider-${openstack_branch}.tar.gz')},
    'placement-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/placement/'
                     'placement-${openstack_branch}.tar.gz')},
    'prometheus-alertmanager': {
        'version': '0.26.0',
        'type': 'url',
        'sha256': {
            'amd64': 'abd73e2ee6bf67d3888699660abbecba7b076bf1f9459a3a8999d493b149ffa6',  # noqa: E501
            'arm64': 'f65969661821570929ad34cf64e034fe72c8e014855d244321c67a0c3ce3fc08'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/alertmanager/'
                     'releases/download/v${version}/'
                     'alertmanager'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-blackbox-exporter': {
        'version': '0.24.0',
        'type': 'url',
        'sha256': {
            'amd64': '81b36cece040491ac0d9995db2a0964c40e24838a03a151c3333a7dc3eef94ff',  # noqa: E501
            'arm64': 'acbbedf03de862fa833bc4dd810e63f105cb44e47abf493192fce3451852dc58'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/blackbox_exporter/'
                     'releases/download/v${version}/'
                     'blackbox_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-cadvisor': {
        'version': '0.47.2',
        'type': 'url',
        'sha256': {
            'amd64': '30602f675e9bcd39b0d4cd4bd9e83c0849dd4bb3a60a0544b9f2a6451a3facfe',  # noqa: E501
            'arm64': 'a15ebac9c60cccbb035e4af83cd45211edac19f3204ed0614b3336fddf91444b'},  # noqa: E501
        'location': ('https://github.com/'
                     'google/cadvisor/'
                     'releases/download/v${version}/'
                     'cadvisor'
                     '-v${version}-linux-${debian_arch}')},
    'prometheus-elasticsearch-exporter': {
        'version': '1.7.0',
        'type': 'url',
        'sha256': {
            'amd64': '45aff83bcea639dc977e34eaa6ad7b1453be96be469f570b39c2d4fc69bf5ffc',  # noqa: E501
            'arm64': '0cf7828f3da1aba73ebef6192ee885345ecd628df782b23aee9c81fa311b92ad'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus-community/elasticsearch_exporter/'
                     'releases/download/v${version}/'
                     'elasticsearch_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-memcached-exporter': {
        'version': '0.13.0',
        'type': 'url',
        'sha256': {
            'amd64': 'ba6a218a36ce121fdcfd403ceb4874d1943903aa5aaa664ada3b953bad3b9f1c',  # noqa: E501
            'arm64': '546a6d40c1e5ece56099e4538de5dfd577fc65d2d5aa3aa507269a203540cb44'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/memcached_exporter/'
                     'releases/download/v${version}/'
                     'memcached_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-msteams': {
        'version': '1.5.2',
        'type': 'url',
        'sha256': {
            'amd64': '0f4df9ee31e655d1ec876ea2c53ab5ae5b07143ef21b9190e61b4d52839e135c'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus-msteams/prometheus-msteams/'
                     'releases/download/v${version}/'
                     'prometheus-msteams'
                     '-linux-${debian_arch}')},
    'prometheus-mtail': {
        'version': '3.0.0-rc52',
        'type': 'url',
        'sha256': {
            'amd64': '96fb8b40579dd281c5c0487d2e1b06350099db82b4539c912370b26198027bc9',  # noqa: E501
            'arm64': 'f7f67545ca2bc7a82bf485287af93af73699e5f86a3a0d5ac2e3c6acdba97baf'},  # noqa: E501
        'location': ('https://github.com/'
                     'google/mtail/'
                     'releases/download/v${version}/'
                     'mtail'
                     '_${version}_linux_${debian_arch}.tar.gz')},
    'prometheus-mysqld-exporter': {
        'version': '0.15.0',
        'type': 'url',
        'sha256': {
            'amd64': '3973db1c46b0323a957a43916b759ee71ddab9096958ce78401fdff894b0dc51',  # noqa: E501
            'arm64': '7de13ac71ac17e345b0da0a97330a81492dc3a811fe8143c90f010b6e012acf8'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/mysqld_exporter/'
                     'releases/download/v${version}/'
                     'mysqld_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-node-exporter': {
        'version': '1.7.0',
        'type': 'url',
        'sha256': {
            'amd64': 'a550cd5c05f760b7934a2d0afad66d2e92e681482f5f57a917465b1fba3b02a6',  # noqa: E501
            'arm64': 'e386c7b53bc130eaf5e74da28efc6b444857b77df8070537be52678aefd34d96'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/node_exporter/'
                     'releases/download/v${version}/'
                     'node_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-openstack-exporter': {
        'version': '1.7.0',
        'type': 'url',
        'sha256': {
            'amd64': 'dfaa0d3dcff22e882d3f61c56bb9ac6f70790df9d67361464159bbb4c7223192',  # noqa: E501
            'arm64': 'd6e0b23fe755732a93796255e3a2be8ec5a699b0a64c21afd377c60ccf60cd55'},  # noqa: E501
        'location': ('https://github.com/'
                     'openstack-exporter/openstack-exporter/'
                     'releases/download/v${version}/'
                     'openstack-exporter'
                     '_${version}_linux_${debian_arch}.tar.gz')},
    'prometheus-ovn-exporter': {
        'version': '1.0.7',
        'type': 'url',
        'sha256': {
            'amd64': '38d9874ddca1581574a7fa0a28ea53447a57dada37bb1385adeb766e6e819de0',  # noqa: E501
            'arm64': 'e03f6a5ab4cf2855a498697026981273ce3c9ff16bd9bb6c97fd7f1344ec2067'},  # noqa: E501
        'location': ('https://github.com/'
                     'greenpau/ovn_exporter/'
                     'releases/download/v${version}/'
                     'ovn-exporter'
                     '_${version}_linux_${debian_arch}.tar.gz')},
    'prometheus-v2-server': {
        'version': '2.48.0',
        'type': 'url',
        'sha256': {
            'amd64': '5871ca9e01ae35bb7ab7a129a845a7a80f0e1453f00f776ac564dd41ff4d754e',  # noqa: E501
            'arm64': 'c6e85f7b4fd0785df48266c1ee53975f862996a99b7d96520dc730e65da7bcf6'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/prometheus/'
                     'releases/download/v${version}/'
                     'prometheus'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'sahara-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara/'
                     'sahara-${openstack_branch}.tar.gz')},
    'sahara-base-plugin-ambari': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-ambari/'
                     'sahara-plugin-ambari-${openstack_branch}.tar.gz')},
    'sahara-base-plugin-cdh': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-cdh/'
                     'sahara-plugin-cdh-${openstack_branch}.tar.gz')},
    'sahara-base-plugin-mapr': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-mapr/'
                     'sahara-plugin-mapr-${openstack_branch}.tar.gz')},
    'sahara-base-plugin-spark': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-spark/'
                     'sahara-plugin-spark-${openstack_branch}.tar.gz')},
    'sahara-base-plugin-storm': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-storm/'
                     'sahara-plugin-storm-${openstack_branch}.tar.gz')},
    'sahara-base-plugin-vanilla': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-vanilla/'
                     'sahara-plugin-vanilla-${openstack_branch}.tar.gz')},
    'senlin-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/senlin/'
                     'senlin-${openstack_branch}.tar.gz')},
    'skyline-apiserver': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/skyline-apiserver/'
                     'skyline-apiserver-${openstack_branch}.tar.gz')},
    'skyline-console': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/skyline-console/'
                     'skyline-console-${openstack_branch}.tar.gz')},
    'solum-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/solum/'
                     'solum-${openstack_branch}.tar.gz')},
    'swift-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/swift/'
                     'swift-${openstack_branch}.tar.gz')},
    'tacker-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tacker/'
                     'tacker-${openstack_branch}.tar.gz')},
    'tacker-base-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-sfc/'
                     'networking-sfc-${openstack_branch}.tar.gz')},
    'trove-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/trove/'
                     'trove-${openstack_branch}.tar.gz')},
    'venus-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/venus/'
                     'venus-${openstack_branch}.tar.gz')},
    'vitrage-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/vitrage/'
                     'vitrage-${openstack_branch}.tar.gz')},
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher/'
                     'watcher-${openstack_branch}.tar.gz')},
    'zun-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zun/'
                     'zun-${openstack_branch}.tar.gz')}
}
