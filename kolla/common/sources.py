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
        'version': 'v4.15.0',
        'type': 'url',
        'sha256': {
            'amd64': 'b26cdc57462124a7aa877f58ad59015ba90fa0b2d8f40e6cbd34408af1e9b607',  # noqa: E501
            'arm64': '0bfb5e245a78e7e20c759c491ecb05aa68ad89024ed5cf710e6e7f4eab90e190'},  # noqa: E501
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
        'version': '0.27.0',
        'type': 'url',
        'sha256': {
            'amd64': '23c3f5a3c73de91dbaec419f3c492bef636deb02680808e5d842e6553aa16074',  # noqa: E501
            'arm64': 'a754304b682cec61f4bd5cfc029b451a30134554b3a2f21a9c487e12814ff8f3'},  # noqa: E501
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
        'version': '0.49.1',
        'type': 'url',
        'sha256': {
            'amd64': '1d5cc701a3fcdf1e8ed1c86da5304b896a6997d9e6673139e78a6f87812495b0',  # noqa: E501
            'arm64': 'c535f46d789599f25c7c680af193d4402da27a98d9828eb2ec916af6256e0c0c'},  # noqa: E501
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
        'version': '0.14.2',
        'type': 'url',
        'sha256': {
            'amd64': '11219035ad3cf63b174d04f52df7188fad8cd7a271631fba97a0e61b4d5e597f',  # noqa: E501
            'arm64': '1790f7c87aa950b5c3d87c7db998be797087699290f5c1dccb16b1b4611056bc'},  # noqa: E501
        'location': ('https://github.com/'
                     'prometheus/memcached_exporter/'
                     'releases/download/v${version}/'
                     'memcached_exporter'
                     '-${version}.linux-${debian_arch}.tar.gz')},
    'prometheus-mtail': {
        'version': '3.0.0-rc54',
        'type': 'url',
        'sha256': {
            'amd64': '6f6cb9c5f2eec6494ecbec9e3f6f0ab9444ef57844143749d7a5b2d2ab1819d6',  # noqa: E501
            'arm64': '6b7049bc44cfe5e90ffeb3ff6cbd2176a3dc7cd9df32ff9e10e1d303d38389e1'},  # noqa: E501
        'location': ('https://github.com/'
                     'google/mtail/'
                     'releases/download/v${version}/'
                     'mtail'
                     '_${version}_linux_${debian_arch}.tar.gz')},
    'prometheus-mysqld-exporter': {
        'version': '0.15.1',
        'type': 'url',
        'sha256': {
            'amd64': '85ea5bc68e1b9f466c1df10ff016652dd210371d42245e012b876265e89ae29d',  # noqa: E501
            'arm64': '8f55c2dcc41aab5998c1e22a2e78e5a940c6894b462736b129fd7bf9b48f8f60'},  # noqa: E501
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
        'version': '2.50.1',
        'type': 'url',
        'sha256': {
            'amd64': '936f3777f8c3a4a90d3c58a6f410350d5932c79367b99771d002bd36e48bd05b',  # noqa: E501
            'arm64': '9f1a65cf08cef3dcd5f0d38d8673ecfaf1054aa9e1e5c18c94efd8546c1fdd96'},  # noqa: E501
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
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher/'
                     'watcher-${openstack_branch}.tar.gz')},
    'zun-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zun/'
                     'zun-${openstack_branch}.tar.gz')}
}
