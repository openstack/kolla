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
        # NOTE(wszumski): Upgrade one minor version at a time:
        # https://etcd.io/docs/v3.4/upgrades/upgrade_3_4/
        'version': '3.5.16',
        'type': 'url',
        'sha256': {
            'amd64': 'b414b27a5ad05f7cb01395c447c85d3227e3fb1c176e51757a283b817f645ccc',  # noqa: E501
            'arm64': '8e68c55e6d72b791a9e98591c755af36f6f55aa9eca63767822cd8a3817fdb23'},  # noqa: E501
        'location': ('https://github.com/etcd-io/etcd/'
                     'releases/download/v${version}'
                     '/etcd-v${version}-linux-${debian_arch}.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/glance/'
                     'glance-${openstack_branch}.tar.gz')},
    'gnocchi-base': {
        'type': 'git',
        'reference': '4.6.4',
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
    'horizon-plugin-fwaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-fwaas-dashboard/'
                     'neutron-fwaas-dashboard-${openstack_branch}.tar.gz')},
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
    'horizon-plugin-neutron-vpnaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas-dashboard/'
                     'neutron-vpnaas-dashboard-${openstack_branch}.tar.gz')},
    'horizon-plugin-octavia-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/octavia-dashboard/'
                     'octavia-dashboard-${openstack_branch}.tar.gz')},
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
        'version': 'v4.20.4',
        'type': 'url',
        'sha256': {
            'amd64': 'fed2cd32fa0042feda44a4a81d73e76f51d692a779f689d3df8082dcadcc73ba',  # noqa: E501
            'arm64': '6bde708d9c8b2e914120772bb6491d7c3dccb7f98746e171ff4c435948f599e1'},  # noqa: E501
        'location': ('https://github.com/go-acme/lego/'
                     'releases/download/${version}/'
                     'lego_${version}_linux_${debian_arch}.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum/'
                     'magnum-${openstack_branch}.tar.gz')},
    'magnum-conductor-plugin-helm': {
        'version': 'v3.16.3',
        'type': 'url',
        'sha256': {
            'amd64': 'f5355c79190951eed23c5432a3b920e071f4c00a64f75e077de0dd4cb7b294ea',  # noqa: E501
            'arm64': '5bd34ed774df6914b323ff84a0a156ea6ff2ba1eaf0113962fa773f3f9def798'},  # noqa: E501
        'location': ('https://get.helm.sh/helm'
                     '-${version}-linux-${debian_arch}.tar.gz')},
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
    'neutron-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron/'
                     'neutron-${openstack_branch}.tar.gz')},
    'neutron-base-plugin-neutron-fwaas': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-fwaas/'
                     'neutron-fwaas-${openstack_branch}.tar.gz')},
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
        'version': '0.28.1',
        'type': 'url',
        'sha256': {
            'amd64': '5ac7ab5e4b8ee5ce4d8fb0988f9cb275efcc3f181b4b408179fafee121693311',  # noqa: E501
            'arm64': 'd8832540e5b9f613d2fd759e31d603173b9c61cc7bb5e3bc7ae2f12038b1ce4f'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/alertmanager/'
                     'releases/download/v${version}/'
                     'alertmanager'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-blackbox-exporter': {
        'version': '0.25.0',
        'type': 'url',
        'sha256': {
            'amd64': 'c651ced6405c5e0cd292a400f47ae9b34f431f16c7bb098afbcd38f710144640',  # noqa: E501
            'arm64': '46ec5a54a41dc1ea8a8cecee637e117de4807d3b0976482a16596e82e79ac484'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/blackbox_exporter/'
                     'releases/download/v${version}/'
                     'blackbox_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-cadvisor': {
        'version': '0.49.2',
        'type': 'url',
        'sha256': {
            'amd64': 'e8273ebfd18bac96834de3eb74a86bda4c2c6d6e9b4c924bdbf1f93e4e0bc24f',  # noqa: E501
            'arm64': '5b852edb911cfe3df7448b03ccbdc6538b6ff00299527864234127cc54f8080f'},  # noqa: E501
        'location': ('https://github.com/'
                     'google/cadvisor/'
                     'releases/download/v${version}/'
                     'cadvisor'
                     '-v${version}-linux-${debian_arch}')},
    'prometheus-elasticsearch-exporter': {
        'version': '1.8.0',
        'type': 'url',
        'sha256': {
            'amd64': 'a03a19d015c45ccc9e35f3a99c6a202b347a521a494cff0e404f9038e426135a',  # noqa: E501
            'arm64': '493ceef304a54e60dfcd0c477d4f0ddad02cfbbb975532f1cb3a169e662f4eea'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus-community/elasticsearch_exporter/'
                     'releases/download/v${version}/'
                     'elasticsearch_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-libvirt-exporter': {
        'version': '1.6.0',
        'type': 'url',
        'sha256': {
            'amd64': '57f1e71ac5bd87f18a40b9089e9fb513dec44ced58328b3065879b279f967596',  # noqa: E501
            'arm64': '8f474fbb515caf19fda92c839eece761738138c7c676d12d10aa0b8c29b3ef9d'},  # noqa: E501
        'location': ('https://github.com/'
                     'inovex/prometheus-libvirt-exporter/'
                     'releases/download/v${version}/'
                     'prometheus-libvirt-exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-memcached-exporter': {
        'version': '0.15.0',
        'type': 'url',
        'sha256': {
            'amd64': 'd628bd8119b8e69696f61bdf6736490962d5abd52d35207b58a547447aa4e74f',  # noqa: E501
            'arm64': '1ec401184ed207c40e8ab8323f46d116f6ff7654ea4040fe0d786af237c5df8d'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/memcached_exporter/'
                     'releases/download/v${version}/'
                     'memcached_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-mtail': {
        'version': '3.0.8',
        'type': 'url',
        'sha256': {
            'amd64': '123c2ee5f48c3eff12ebccee38befd2233d715da736000ccde49e3d5607724e4',  # noqa: E501
            'arm64': 'aa04811c0929b6754408676de520e050c45dddeb3401881888a092c9aea89cae'},  # noqa: E501
        'location': ('https://github.com/'
                     'google/mtail/'
                     'releases/download/v${version}/'
                     'mtail'
                     '_${version}_linux_${debian_arch}.tar.gz')},
    'prometheus-mysqld-exporter': {
        'version': '0.16.0',
        'type': 'url',
        'sha256': {
            'amd64': '32fe0b59ef3f52624a1958aaf6b8855f27c2b492a7026d62a975bbd251be209d',  # noqa: E501
            'arm64': '9ffc6e107bd122e68a95fa5c194bc3fc257104fef6ed720a26a240cd608c777b'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/mysqld_exporter/'
                     'releases/download/v${version}/'
                     'mysqld_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-node-exporter': {
        'version': '1.8.2',
        'type': 'url',
        'sha256': {
            'amd64': '6809dd0b3ec45fd6e992c19071d6b5253aed3ead7bf0686885a51d85c6643c66',  # noqa: E501
            'arm64': '627382b9723c642411c33f48861134ebe893e70a63bcc8b3fc0619cd0bfac4be'},  # noqa: E501
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
    'prometheus-server': {
        'version': '3.2.1',
        'type': 'url',
        'sha256': {
            'amd64': 'a622e3007c9109a7f470e1433cbd29bf392596715cf7eea8b81b37fa9d26b7be',  # noqa: E501
            'arm64': 'f2dec3178f1181c1b795b275750d056e71ead13f7fbfe08b76834c4ec20b748e'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/prometheus/'
                     'releases/download/v${version}/'
                     'prometheus'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'skyline-apiserver': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/skyline-apiserver/'
                     'skyline-apiserver-${openstack_branch}.tar.gz')},
    'skyline-console': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/skyline-console/'
                     'skyline-console-${openstack_branch}.tar.gz')},
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
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher/'
                     'watcher-${openstack_branch}.tar.gz')},
    'zun-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zun/'
                     'zun-${openstack_branch}.tar.gz')}
}
