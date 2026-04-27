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
        # https://etcd.io/docs/v3.6/upgrades/upgrade_3_6/
        'version': '3.6.5',
        'type': 'url',
        'sha256': {
            'amd64': '66bad39ed920f6fc15fd74adcb8bfd38ba9a6412f8c7852d09eb11670e88cac3',  # noqa: E501
            'arm64': '7010161787077b07de29b15b76825ceacbbcedcb77fe2e6832f509be102cab6b'},  # noqa: E501
        'location': ('https://github.com/etcd-io/etcd/'
                     'releases/download/v${version}'
                     '/etcd-v${version}-linux-${debian_arch}.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/glance/'
                     'glance-${openstack_branch}.tar.gz')},
    'gnocchi-base': {
        'type': 'git',
        'reference': '4.7.0',
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
    'horizon-plugin-watcher-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher-dashboard/'
                     'watcher-dashboard-${openstack_branch}.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic/'
                     'ironic-${openstack_branch}.tar.gz')},
    'ironic-conductor-plugin-prometheus-exporter': {
        'type': 'url',
        'location': (
            '$tarballs_base/openstack/ironic-prometheus-exporter/'
            'ironic-prometheus-exporter-${openstack_branch}.tar.gz')},
    'keystone-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/keystone/'
                     'keystone-${openstack_branch}.tar.gz')},
    'kolla-toolbox': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/requirements/'
                     'requirements-${openstack_branch}.tar.gz')},
    'letsencrypt-lego': {
        'version': 'v4.27.0',
        'type': 'url',
        'sha256': {
            'amd64': '898b58bbbca4282d706b4f204593cb94fc2ed13232777236c06dc20259bbcd02',  # noqa: E501
            'arm64': '2973b412d37e5d652a91bda1a6bf7642491e316bc0f855a614e2c996249014dc'},  # noqa: E501
        'location': ('https://github.com/go-acme/lego/'
                     'releases/download/${version}/'
                     'lego_${version}_linux_${debian_arch}.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum/'
                     'magnum-${openstack_branch}.tar.gz')},
    'magnum-conductor-plugin-helm': {
        'version': 'v3.19.0',
        'type': 'url',
        'sha256': {
            'amd64': 'a7f81ce08007091b86d8bd696eb4d86b8d0f2e1b9f6c714be62f82f96a594496',  # noqa: E501
            'arm64': '440cf7add0aee27ebc93fada965523c1dc2e0ab340d4348da2215737fc0d76ad'},  # noqa: E501
        'location': ('https://get.helm.sh/helm'
                     '-${version}-linux-${debian_arch}.tar.gz')},
    'manila-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/manila/'
                     'manila-${openstack_branch}.tar.gz')},
    'mariadb-server-plugin-mariadb-docker': {
        # NOTE(seunghun1ee): This repo is needed to get MariaDB healthcheck.sh
        'type': 'git',
        'reference': 'master',
        'location': ('https://github.com/MariaDB/mariadb-docker')},
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
        'version': '0.31.1',
        'type': 'url',
        'sha256': {
            'amd64': '35191cbd9d4f8162458b78dd7e93990cccd246044d9a6f788adb1c66ac3ea07b',  # noqa: E501
            'arm64': '266dda88b64318c27847ef9af4ff450fc178c827550a8039420c5ca8657a4a8b'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/alertmanager/'
                     'releases/download/v${version}/'
                     'alertmanager'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-blackbox-exporter': {
        'version': '0.28.0',
        'type': 'url',
        'sha256': {
            'amd64': 'caf5d242fb1cf6d5cb678f3f799f22703d4fafea26b03dcbbd7e1f1825e06329',  # noqa: E501
            'arm64': '63312be0983d85e5109710a7dc93df3051157ae581853fa3655d171cc1b2806e'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/blackbox_exporter/'
                     'releases/download/v${version}/'
                     'blackbox_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-cadvisor': {
        'version': '0.56.2',
        'type': 'url',
        'sha256': {
            'amd64': 'ad92930f16a2f9da15190675e09eeaceb8fd38637d07a686bb0dd68695f692af',  # noqa: E501
            'arm64': 'b7a707379496fd7a7b5d2768c5c494427112f534ba5069f889af28ffe6ad11bb'},  # noqa: E501
        'location': ('https://github.com/'
                     'google/cadvisor/'
                     'releases/download/v${version}/'
                     'cadvisor'
                     '-v${version}-linux-${debian_arch}')},
    'prometheus-elasticsearch-exporter': {
        'version': '1.10.0',
        'type': 'url',
        'sha256': {
            'amd64': '1dcf288082a25b2741e98da6c9fc012b6c821696a26c6ac57c20042f24714a74',  # noqa: E501
            'arm64': '0ff4753a975eb5611c03123d565e8aaa84e4c05f698ce0a2d6c0f437a14bfe34'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus-community/elasticsearch_exporter/'
                     'releases/download/v${version}/'
                     'elasticsearch_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-libvirt-exporter': {
        'version': '2.3.1',
        'type': 'url',
        'sha256': {
            'amd64': '2e1657d10291059f420a467cbe3363c7353bbce9d5445f0d8d302bd96caaf0a8',  # noqa: E501
            'arm64': '676dc76766ce4a2eaa8324a3aca8cfe89711536337d3b5b862ddf141fb57a224'},  # noqa: E501
        'location': ('https://github.com/'
                     'inovex/prometheus-libvirt-exporter/'
                     'releases/download/v${version}/'
                     'prometheus-libvirt-exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-memcached-exporter': {
        'version': '0.15.5',
        'type': 'url',
        'sha256': {
            'amd64': '5b82e6579b77fae00683d10d5923329173925a5abd95a799f5489a66136b884c',  # noqa: E501
            'arm64': '609e6d7484f22fd9e405c0022a9e2d7f86eedef1cfa55772231528271082aeae'},  # noqa: E501
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
        'version': '0.18.0',
        'type': 'url',
        'sha256': {
            'amd64': '46e8f45654352bdd42d162b2b4a68f00055d45acc168f9c068235b9e3acc39c1',  # noqa: E501
            'arm64': 'abdb452600ca086b68244aadf8045fbf0b6a48dcb76eed5576995806c176f6ce'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/mysqld_exporter/'
                     'releases/download/v${version}/'
                     'mysqld_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-node-exporter': {
        'version': '1.10.2',
        'type': 'url',
        'sha256': {
            'amd64': 'c46e5b6f53948477ff3a19d97c58307394a29fe64a01905646f026ddc32cb65b',  # noqa: E501
            'arm64': 'de69ec8341c8068b7c8e4cfe3eb85065d24d984a3b33007f575d307d13eb89a6'},  # noqa: E501
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
    'prometheus-openstack-network-exporter': {
        'version': '0.2.0',
        'type': 'url',
        'sha256': {
            'amd64': 'c93e6c62a0b861af50292f51b1443114e2178d89450b37cb0462723eaa3b2338',  # noqa: E501
            'arm64': '478de6e005188d0e2545e34ca2c5b93a33a32dc7d1f1b03dc3210c4ef7e44305'},  # noqa: E501
        'location': ('https://github.com/'
                     'openstack-k8s-operators/openstack-network-exporter/'
                     'releases/download/v${version}/'
                     'openstack-network-exporter'
                     '-linux-${debian_arch}')},
    'prometheus-server': {
        'version': '3.5.2',
        'type': 'url',
        'sha256': {
            'amd64': '552c6d701e27d3c77983bb8a76e61953cb60021f6e10f17a929546a6dedc436a',  # noqa: E501
            'arm64': '06a77b3f580b0db0f41e1c52274503b609db58660e44577facb0ee53e4ff8b27'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/prometheus/'
                     'releases/download/v${version}/'
                     'prometheus'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-valkey-exporter': {
        'version': '1.82.0',
        'type': 'url',
        'sha256': {
            'amd64': '2d98dd0888f46e206bf3ad1b7c1784934a3a39cd8774cf47615f4c15594547cd',  # noqa: E501
            'arm64': '13aaa6acbb145848cb97ed3bab22747e094b3f0ed22df83c8ace593e3c527c95'},  # noqa: E501
        'location': ('https://github.com/'
                     'oliver006/redis_exporter/'
                     'releases/download/v${version}/'
                     'redis_exporter'
                     '-v${version}.linux-${debian_arch}.tar.gz')},
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
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher/'
                     'watcher-${openstack_branch}.tar.gz')}
}
