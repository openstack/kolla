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
        'reference': '4.4.2',
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
    # FIXME(mgoddard): Revert to ${openstack_branch} when a stable-yoga tarball
    # exists.
    'venus-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/venus/'
                     'venus-master.tar.gz')},
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
