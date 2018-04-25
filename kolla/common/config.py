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

import itertools
import os

from oslo_config import cfg
from oslo_config import types

from kolla.version import version_info as version


BASE_OS_DISTRO = ['centos', 'rhel', 'ubuntu', 'oraclelinux', 'debian']
BASE_ARCH = ['x86_64', 'ppc64le', 'aarch64']
DEFAULT_BASE_TAGS = {
    'centos': '7',
    'rhel': '7',
    'oraclelinux': '7-slim',
    'debian': 'stretch-backports',
    'ubuntu': '18.04',
}
DISTRO_RELEASE = {
    'centos': '7',
    'rhel': '7',
    'oraclelinux': '7',
    'debian': 'stretch-backports',
    'ubuntu': '18.04',
}

# This is noarch repository so we will use it on all architectures
DELOREAN = \
    "https://trunk.rdoproject.org/centos7/current-passed-ci/delorean.repo"
DELOREAN_DEPS = "https://trunk.rdoproject.org/centos7/delorean-deps.repo"

INSTALL_TYPE_CHOICES = ['binary', 'source', 'rdo', 'rhos']

TARBALLS_BASE = "http://tarballs.openstack.org"

_PROFILE_OPTS = [
    cfg.ListOpt('infra',
                default=[
                    'ceph',
                    'certmonger',
                    'cron',
                    'elasticsearch',
                    'etcd',
                    'fluentd',
                    'haproxy',
                    'keepalived',
                    'kibana',
                    'kolla-toolbox',
                    'logstash',
                    'mariadb',
                    'memcached',
                    'mongodb',
                    'opendaylight',
                    'openvswitch',
                    'ptp',
                    'qdrouterd',
                    'rabbitmq',
                    'redis',
                    'rsyslog',
                    'skydive',
                    'storm',
                    'tgtd',
                ],
                help='Infra images'),
    cfg.ListOpt('main',
                default=[
                    'ceilometer',
                    'cinder',
                    'glance',
                    'heat',
                    'horizon',
                    'iscsi',
                    'keystone',
                    'neutron',
                    'nova-',
                    'swift',
                ],
                help='Main images'),
    cfg.ListOpt('aux',
                default=[
                    'almanach',
                    'aodh',
                    'blazar',
                    'cloudkitty',
                    'congress',
                    'designate',
                    'dragonflow',
                    'ec2-api',
                    'freezer',
                    'gnocchi',
                    'influxdb',
                    'ironic',
                    'kafka',
                    'karbor',
                    'kuryr',
                    'magnum',
                    'manila',
                    'mistral',
                    'monasca',
                    'murano',
                    'novajoin',
                    'octavia',
                    'panko',
                    'rally',
                    'redis',
                    'sahara',
                    'searchlight',
                    'senlin',
                    'solum',
                    'tacker',
                    'telegraf',
                    'trove',
                    'vitrage',
                    'zaqar',
                    'zookeeper',
                    'zun',
                ],
                help='Aux Images'),
    cfg.ListOpt('default',
                default=[
                    'chrony',
                    'cron',
                    'kolla-toolbox',
                    'fluentd',
                    'glance',
                    'haproxy',
                    'heat',
                    'horizon',
                    'keepalived',
                    'keystone',
                    'mariadb',
                    'memcached',
                    'neutron',
                    'nova-',
                    'openvswitch',
                    'rabbitmq',
                ],
                help='Default images'),
    cfg.ListOpt('gate',
                default=[
                    'chrony',
                    'cron',
                    'fluentd',
                    'glance',
                    'haproxy',
                    'horizon',
                    'keepalived',
                    'keystone',
                    'kolla-toolbox',
                    'mariadb',
                    'memcached',
                    'neutron',
                    'nova-',
                    'openvswitch',
                    'rabbitmq',
                ],
                help='Gate images')
]

hostarch = os.uname()[4]

_CLI_OPTS = [
    cfg.StrOpt('base', short='b', default='centos',
               choices=BASE_OS_DISTRO,
               help='The distro type of the base image.'),
    cfg.StrOpt('base-tag', default='latest',
               help='The base distro image tag'),
    cfg.StrOpt('base-image',
               help='The base image name. Default is the same with base.'),
    cfg.StrOpt('base-arch', default=hostarch,
               choices=BASE_ARCH,
               help='The base architecture. Default is same as host'),
    cfg.BoolOpt('debug', short='d', default=False,
                help='Turn on debugging log level'),
    cfg.BoolOpt('skip-parents', default=False,
                help='Do not rebuild parents of matched images'),
    cfg.BoolOpt('skip-existing', default=False,
                help='Do not rebuild images present in the docker cache'),
    cfg.DictOpt('build-args',
                help='Set docker build time variables'),
    cfg.BoolOpt('keep', default=False,
                help='Keep failed intermediate containers'),
    cfg.BoolOpt('list-dependencies', short='l',
                help='Show image dependencies (filtering supported)'),
    cfg.BoolOpt('list-images',
                help='Show all available images (filtering supported)'),
    cfg.StrOpt('namespace', short='n', default='kolla',
               help='The Docker namespace name'),
    cfg.StrOpt('network_mode', default=None,
               help='The network mode for Docker build. Example: host'),
    cfg.BoolOpt('cache', default=True,
                help='Use the Docker cache when building'),
    cfg.MultiOpt('profile', types.String(), short='p',
                 help=('Build a pre-defined set of images, see [profiles]'
                       ' section in config. The default profiles are:'
                       ' {}'.format(', '.join(
                           [opt.name for opt in _PROFILE_OPTS])
                       ))),
    cfg.BoolOpt('push', default=False,
                help='Push images after building'),
    cfg.IntOpt('push-threads', default=1, min=1,
               help=('The number of threads to user while pushing'
                     ' Images. Note: Docker can not handle threading'
                     ' push properly')),
    cfg.IntOpt('retries', short='r', default=3, min=0,
               help='The number of times to retry while building'),
    cfg.MultiOpt('regex', types.String(), positional=True,
                 help=('Build only images matching regex and its'
                       ' dependencies')),
    cfg.StrOpt('registry',
               help=('The docker registry host. The default registry host'
                     ' is Docker Hub')),
    cfg.StrOpt('save-dependency',
               help=('Path to the file to store the docker image'
                     ' dependency in Graphviz dot format')),
    cfg.StrOpt('format', short='f', default='json',
               choices=['json', 'none'],
               help='Format to write the final results in'),
    cfg.StrOpt('tarballs-base', default=TARBALLS_BASE,
               help='Base url to OpenStack tarballs'),
    cfg.StrOpt('type', short='t', default='binary',
               choices=INSTALL_TYPE_CHOICES,
               dest='install_type',
               help=('The method of the OpenStack install.')),
    cfg.IntOpt('threads', short='T', default=8, min=1,
               help=('The number of threads to use while building.'
                     ' (Note: setting to one will allow real time'
                     ' logging)')),
    cfg.StrOpt('tag', default=version.cached_version_string(),
               help='The Docker tag'),
    cfg.BoolOpt('template-only', default=False,
                help="Don't build images. Generate Dockerfile only"),
    cfg.IntOpt('timeout', default=120,
               help='Time in seconds after which any operation times out'),
    cfg.MultiOpt('template-override', types.String(),
                 help='Path to template override file'),
    cfg.MultiOpt('docker-dir', types.String(),
                 help='Path to additional docker file template directory',
                 short='D', default=[]),
    cfg.StrOpt('logs-dir', help='Path to logs directory'),
    cfg.BoolOpt('pull', default=True,
                help='Attempt to pull a newer version of the base image'),
    cfg.StrOpt('work-dir', help=('Path to be used as working directory.'
                                 ' By default, a temporary dir is created')),
    cfg.BoolOpt('squash', default=False,
                help=('Squash the image layers. WARNING: it will consume lots'
                      ' of disk IO. "docker-squash" tool is required, install'
                      ' it by "pip install docker-squash"')),
]

_BASE_OPTS = [
    cfg.StrOpt('maintainer',
               default='Kolla Project (https://launchpad.net/kolla)',
               help='Content of the maintainer label'),
    cfg.ListOpt('rpm_setup_config', default=[DELOREAN, DELOREAN_DEPS],
                help=('Comma separated list of .rpm or .repo file(s) '
                      'or URL(s) to install before building containers')),
    cfg.StrOpt('apt_sources_list', help=('Path to custom sources.list')),
    cfg.StrOpt('apt_preferences', help=('Path to custom apt/preferences')),
    cfg.BoolOpt('squash-cleanup', default=True,
                help='Remove source image from Docker after squashing'),
    cfg.StrOpt('squash-tmp-dir',
               help='Temporary directory to be used during squashing')
]


SOURCES = {
    'openstack-base': {
        'type': 'url',
        'location': ('$tarballs_base/requirements/'
                     'requirements-master.tar.gz')},
    'almanach-base': {
        'type': 'url',
        'location': ('$tarballs_base/almanach/'
                     'almanach-master.tar.gz')},
    'aodh-base': {
        'type': 'url',
        'location': ('$tarballs_base/aodh/'
                     'aodh-master.tar.gz')},
    'barbican-base': {
        'type': 'url',
        'location': ('$tarballs_base/barbican/'
                     'barbican-master.tar.gz')},
    'bifrost-base': {
        'type': 'url',
        'location': ('$tarballs_base/bifrost/'
                     'bifrost-master.tar.gz')},
    'blazar-base': {
        'type': 'url',
        'location': ('$tarballs_base/blazar/'
                     'blazar-master.tar.gz')},
    'ceilometer-base': {
        'type': 'url',
        'location': ('$tarballs_base/ceilometer/'
                     'ceilometer-master.tar.gz')},
    'ceilometer-base-plugin-panko': {
        'type': 'url',
        'location': ('$tarballs_base/panko/'
                     'panko-master.tar.gz')},
    'cinder-base': {
        'type': 'url',
        'location': ('$tarballs_base/cinder/'
                     'cinder-master.tar.gz')},
    'congress-base': {
        'type': 'url',
        'location': ('$tarballs_base/congress/'
                     'congress-master.tar.gz')},
    'cloudkitty-base': {
        'type': 'url',
        'location': ('$tarballs_base/cloudkitty/'
                     'cloudkitty-master.tar.gz')},
    'designate-base': {
        'type': 'url',
        'location': ('$tarballs_base/designate/'
                     'designate-master.tar.gz')},
    'dragonflow-base': {
        'type': 'url',
        'location': ('$tarballs_base/dragonflow/'
                     'dragonflow-master.tar.gz')},
    'ec2-api': {
        'type': 'url',
        'location': ('$tarballs_base/ec2-api/'
                     'ec2-api-master.tar.gz')},
    'freezer-api': {
        'type': 'url',
        'location': ('$tarballs_base/freezer-api/'
                     'freezer-api-master.tar.gz')},
    'freezer-base': {
        'type': 'url',
        'location': ('$tarballs_base/freezer/'
                     'freezer-master.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('$tarballs_base/glance/'
                     'glance-master.tar.gz')},
    'gnocchi-base': {
        'type': 'git',
        'reference': 'master',
        'location': ('https://github.com/gnocchixyz/'
                     'gnocchi.git')},
    'heat-base': {
        'type': 'url',
        'location': ('$tarballs_base/heat/'
                     'heat-master.tar.gz')},
    'horizon': {
        'type': 'url',
        'location': ('$tarballs_base/horizon/'
                     'horizon-master.tar.gz')},
    'horizon-plugin-blazar-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/blazar-dashboard/'
                     'blazar-dashboard-master.tar.gz')},
    'horizon-plugin-congress-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/congress-dashboard/'
                     'congress-dashboard-master.tar.gz')},
    'horizon-plugin-cloudkitty-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/cloudkitty-dashboard/'
                     'cloudkitty-dashboard-master.tar.gz')},
    'horizon-plugin-designate-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/designate-dashboard/'
                     'designate-dashboard-master.tar.gz')},
    'horizon-plugin-fwaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-fwaas-dashboard/'
                     'neutron-fwaas-dashboard-master.tar.gz')},
    'horizon-plugin-freezer-web-ui': {
        'type': 'url',
        'location': ('$tarballs_base/freezer-web-ui/'
                     'freezer-web-ui-master.tar.gz')},
    'horizon-plugin-heat-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/heat-dashboard/'
                     'heat-dashboard-master.tar.gz')},
    'horizon-plugin-ironic-ui': {
        'type': 'url',
        'location': ('$tarballs_base/ironic-ui/'
                     'ironic-ui-master.tar.gz')},
    'horizon-plugin-karbor-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/karbor-dashboard/'
                     'karbor-dashboard-master.tar.gz')},
    'horizon-plugin-magnum-ui': {
        'type': 'url',
        'location': ('$tarballs_base/magnum-ui/'
                     'magnum-ui-master.tar.gz')},
    'horizon-plugin-manila-ui': {
        'type': 'url',
        'location': ('$tarballs_base/manila-ui/'
                     'manila-ui-master.tar.gz')},
    'horizon-plugin-mistral-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/mistral-dashboard/'
                     'mistral-dashboard-master.tar.gz')},
    'horizon-plugin-monasca-ui': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-ui/'
                     'monasca-ui-master.tar.gz')},
    'horizon-plugin-murano-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/murano-dashboard/'
                     'murano-dashboard-master.tar.gz')},
    'horizon-plugin-neutron-lbaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-lbaas-dashboard/'
                     'neutron-lbaas-dashboard-master.tar.gz')},
    'horizon-plugin-neutron-vpnaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-vpnaas-dashboard/'
                     'neutron-vpnaas-dashboard-master.tar.gz')},
    'horizon-plugin-octavia-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/octavia-dashboard/'
                     'octavia-dashboard-master.tar.gz')},
    'horizon-plugin-sahara-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/sahara-dashboard/'
                     'sahara-dashboard-master.tar.gz')},
    'horizon-plugin-searchlight-ui': {
        'type': 'url',
        'location': ('$tarballs_base/searchlight-ui/'
                     'searchlight-ui-master.tar.gz')},
    'horizon-plugin-senlin-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/senlin-dashboard/'
                     'senlin-dashboard-master.tar.gz')},
    'horizon-plugin-solum-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/solum-dashboard/'
                     'solum-dashboard-master.tar.gz')},
    'horizon-plugin-tacker-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/tacker-horizon/'
                     'tacker-horizon-master.tar.gz')},
    'horizon-plugin-trove-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/trove-dashboard/'
                     'trove-dashboard-master.tar.gz')},
    'horizon-plugin-vitrage-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/vitrage-dashboard/'
                     'vitrage-dashboard-master.tar.gz')},
    'horizon-plugin-watcher-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/watcher-dashboard/'
                     'watcher-dashboard-master.tar.gz')},
    'horizon-plugin-zaqar-ui': {
        'type': 'url',
        'location': ('$tarballs_base/zaqar-ui/'
                     'zaqar-ui-master.tar.gz')},
    'horizon-plugin-zun-ui': {
        'type': 'url',
        'location': ('$tarballs_base/zun-ui/'
                     'zun-ui-master.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('$tarballs_base/ironic/'
                     'ironic-master.tar.gz')},
    'ironic-inspector': {
        'type': 'url',
        'location': ('$tarballs_base/ironic-inspector/'
                     'ironic-inspector-master.tar.gz')},
    'karbor-base': {
        'type': 'url',
        'location': ('$tarballs_base/karbor/'
                     'karbor-master.tar.gz')},
    'keystone-base': {
        'type': 'url',
        'location': ('$tarballs_base/keystone/'
                     'keystone-master.tar.gz')},
    'kuryr-base': {
        'type': 'url',
        'location': ('$tarballs_base/kuryr/'
                     'kuryr-master.tar.gz')},
    'kuryr-libnetwork': {
        'type': 'url',
        'location': ('$tarballs_base/kuryr-libnetwork/'
                     'kuryr-libnetwork-master.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('$tarballs_base/magnum/'
                     'magnum-master.tar.gz')},
    'manila-base': {
        'type': 'url',
        'location': ('$tarballs_base/manila/'
                     'manila-master.tar.gz')},
    'mistral-base': {
        'type': 'url',
        'location': ('$tarballs_base/mistral/'
                     'mistral-master.tar.gz')},
    'mistral-base-plugin-tacker': {
        'type': 'url',
        'location': ('$tarballs_base/tacker/'
                     'tacker-master.tar.gz')},
    'monasca-api': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-api/'
                     'monasca-api-master.tar.gz')},
    'monasca-log-api': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-log-api/'
                     'monasca-log-api-master.tar.gz')},
    'monasca-notification': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-notification/'
                     'monasca-notification-master.tar.gz')},
    'monasca-persister': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-persister/'
                     'monasca-persister-master.tar.gz')},
    'monasca-statsd': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-statsd/'
                     'monasca-statsd-master.tar.gz')},
    # FIXME(dszumski): Use openstack tar when infra is fixed
    'monasca-thresh': {
        'type': 'url',
        'location': ('https://github.com/openstack/monasca-thresh/archive/'
                     'master.tar.gz')},
    'monasca-thresh-additions-monasca-common': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-common/'
                     'monasca-common-master.tar.gz')},
    'murano-base': {
        'type': 'url',
        'location': ('$tarballs_base/murano/'
                     'murano-master.tar.gz')},
    'neutron-base': {
        'type': 'url',
        'location': ('$tarballs_base/neutron/'
                     'neutron-master.tar.gz')},
    'neutron-base-plugin-neutron-fwaas': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-fwaas/'
                     'neutron-fwaas-master.tar.gz')},
    'neutron-base-plugin-networking-ansible': {
        'type': 'url',
        'location': ('$tarballs_base/networking-ansible/'
                     'networking-ansible-master.tar.gz')},
    'neutron-base-plugin-networking-baremetal': {
        'type': 'url',
        'location': ('$tarballs_base/networking-baremetal/'
                     'networking-baremetal-master.tar.gz')},
    'neutron-base-plugin-networking-generic-switch': {
        'type': 'url',
        'location': ('$tarballs_base/networking-generic-switch/'
                     'networking-generic-switch-master.tar.gz')},
    'neutron-base-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/networking-sfc/'
                     'networking-sfc-master.tar.gz')},
    'neutron-base-plugin-vmware-nsx': {
        'type': 'url',
        'location': ('$tarballs_base/vmware-nsx/'
                     'vmware-nsx-master.tar.gz')},
    'neutron-base-plugin-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-vpnaas/'
                     'neutron-vpnaas-master.tar.gz')},
    'neutron-bgp-dragent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-dynamic-routing/'
                     'neutron-dynamic-routing-master.tar.gz')},
    'neutron-lbaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-lbaas/'
                     'neutron-lbaas-master.tar.gz')},
    'neutron-server-opendaylight-plugin-ceilometer': {
        'type': 'url',
        'location': ('$tarballs_base/ceilometer/'
                     'ceilometer-master.tar.gz')},
    'neutron-server-opendaylight-plugin-networking-odl': {
        'type': 'url',
        'location': ('$tarballs_base/networking-odl/'
                     'networking-odl-master.tar.gz')},
    'neutron-server-opendaylight-plugin-networking-bgpvpn': {
        'type': 'url',
        'location': ('$tarballs_base/networking-bgpvpn/'
                     'networking-bgpvpn-master.tar.gz')},
    'neutron-server-opendaylight-plugin-networking-l2gw': {
        'type': 'url',
        'location': ('$tarballs_base/networking-l2gw/'
                     'networking-l2gw-master.tar.gz')},
    'neutron-server-opendaylight-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/networking-sfc/'
                     'networking-sfc-master.tar.gz')},
    'neutron-server-plugin-networking-infoblox': {
        'type': 'url',
        'location': ('$tarballs_base/networking-infoblox/'
                     'networking-infoblox-master.tar.gz')},
    'neutron-server-plugin-neutron-dynamic-routing': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-dynamic-routing/'
                     'neutron-dynamic-routing-master.tar.gz')},
    'neutron-server-plugin-neutron-lbaas': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-lbaas/'
                     'neutron-lbaas-master.tar.gz')},
    'neutron-server-plugin-vmware-nsxlib': {
        'type': 'url',
        'location': ('$tarballs_base/vmware-nsxlib/'
                     'vmware-nsxlib-master.tar.gz')},
    'neutron-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-vpnaas/'
                     'neutron-vpnaas-master.tar.gz')},
    'neutron-server-ovn-plugin-networking-ovn': {
        'type': 'url',
        'location': ('$tarballs_base/networking-ovn/'
                     'networking-ovn-master.tar.gz')},
    'neutron-metadata-agent-ovn-plugin-networking-ovn': {
        'type': 'url',
        'location': ('$tarballs_base/networking-ovn/'
                     'networking-ovn-master.tar.gz')},
    'nova-base': {
        'type': 'url',
        'location': ('$tarballs_base/nova/'
                     'nova-master.tar.gz')},
    'nova-base-plugin-blazar': {
        'type': 'url',
        'location': ('$tarballs_base/blazar-nova/'
                     'blazar-nova-master.tar.gz')},
    'nova-base-plugin-mksproxy': {
        'type': 'url',
        'location': ('$tarballs_base/nova-mksproxy/'
                     'nova-mksproxy-master.tar.gz')},
    'novajoin-base': {
        'type': 'url',
        'location': ('$tarballs_base/novajoin/'
                     'novajoin-master.tar.gz')},
    'octavia-base': {
        'type': 'url',
        'location': ('$tarballs_base/octavia/'
                     'octavia-master.tar.gz')},
    'panko-base': {
        'type': 'url',
        'location': ('$tarballs_base/panko/'
                     'panko-master.tar.gz')},
    'tempest-plugin-tempest-conf': {
        'type': 'url',
        'location': ('$tarballs_base/python-tempestconf/'
                     'python-tempestconf-master.tar.gz')},
    'tempest-plugin-barbican': {
        'type': 'url',
        'location': ('$tarballs_base/barbican-tempest-plugin/'
                     'barbican-tempest-plugin-master.tar.gz')},
    'tempest-plugin-blazar': {
        'type': 'url',
        'location': ('$tarballs_base/blazar-tempest-plugin/'
                     'blazar-tempest-plugin-master.tar.gz')},
    'tempest-plugin-cinder': {
        'type': 'url',
        'location': ('$tarballs_base/cinder-tempest-plugin/'
                     'cinder-tempest-plugin-master.tar.gz')},
    'tempest-plugin-congress': {
        'type': 'url',
        'location': ('$tarballs_base/congress-tempest-plugin/'
                     'congress-tempest-plugin-master.tar.gz')},
    'tempest-plugin-ec2api': {
        'type': 'url',
        'location': ('$tarballs_base/ec2api-tempest-plugin/'
                     'ec2api-tempest-plugin-master.tar.gz')},
    'tempest-plugin-heat': {
        'type': 'url',
        'location': ('$tarballs_base/heat-tempest-plugin/'
                     'heat-tempest-plugin-master.tar.gz')},
    'tempest-plugin-ironic': {
        'type': 'url',
        'location': ('$tarballs_base/ironic-tempest-plugin/'
                     'ironic-tempest-plugin-master.tar.gz')},
    'tempest-plugin-keystone': {
        'type': 'url',
        'location': ('$tarballs_base/keystone-tempest-plugin/'
                     'keystone-tempest-plugin-master.tar.gz')},
    'tempest-plugin-magnum': {
        'type': 'url',
        'location': ('$tarballs_base/magnum-tempest-plugin/'
                     'magnum-tempest-plugin-master.tar.gz')},
    'tempest-plugin-manila': {
        'type': 'url',
        'location': ('$tarballs_base/manila-tempest-plugin/'
                     'manila-tempest-plugin-master.tar.gz')},
    'tempest-plugin-mistral': {
        'type': 'url',
        'location': ('$tarballs_base/mistral-tempest-plugin/'
                     'mistral-tempest-plugin-master.tar.gz')},
    'tempest-plugin-monasca': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-tempest-plugin/'
                     'monasca-tempest-plugin-master.tar.gz')},
    'tempest-plugin-murano': {
        'type': 'url',
        'location': ('$tarballs_base/murano-tempest-plugin/'
                     'murano-tempest-plugin-master.tar.gz')},
    'tempest-plugin-neutron': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-tempest-plugin/'
                     'neutron-tempest-plugin-master.tar.gz')},
    'tempest-plugin-patrole': {
        'type': 'url',
        'location': ('$tarballs_base/patrole/'
                     'patrole-master.tar.gz')},
    'tempest-plugin-telemetry': {
        'type': 'url',
        'location': ('$tarballs_base/telemetry-tempest-plugin/'
                     'telemetry-tempest-plugin-master.tar.gz')},
    'tempest-plugin-tripleo-common': {
        'type': 'url',
        'location': ('$tarballs_base/tripleo-common-tempest-plugin/'
                     'tripleo-common-tempest-plugin-master.tar.gz')},
    'tempest-plugin-trove': {
        'type': 'url',
        'location': ('$tarballs_base/trove-tempest-plugin/'
                     'trove-tempest-plugin-master.tar.gz')},
    'tempest-plugin-vitrage': {
        'type': 'url',
        'location': ('$tarballs_base/vitrage-tempest-plugin/'
                     'vitrage-tempest-plugin-master.tar.gz')},
    'tempest-plugin-watcher': {
        'type': 'url',
        'location': ('$tarballs_base/watcher-tempest-plugin/'
                     'watcher-tempest-plugin-master.tar.gz')},
    'tempest-plugin-zaqar': {
        'type': 'url',
        'location': ('$tarballs_base/zaqar-tempest-plugin/'
                     'zaqar-tempest-plugin-master.tar.gz')},
    'rally': {
        'type': 'url',
        'location': ('$tarballs_base/rally/'
                     'rally-master.tar.gz')},
    'sahara-base': {
        'type': 'url',
        'location': ('$tarballs_base/sahara/'
                     'sahara-master.tar.gz')},
    'searchlight-base': {
        'type': 'url',
        'location': ('$tarballs_base/searchlight/'
                     'searchlight-master.tar.gz')},
    'senlin-base': {
        'type': 'url',
        'location': ('$tarballs_base/senlin/'
                     'senlin-master.tar.gz')},
    'solum-base': {
        'type': 'url',
        'location': ('$tarballs_base/solum/'
                     'solum-master.tar.gz')},
    'swift-base': {
        'type': 'url',
        'location': ('$tarballs_base/swift/'
                     'swift-master.tar.gz')},
    'tacker-base': {
        'type': 'url',
        'location': ('$tarballs_base/tacker/'
                     'tacker-master.tar.gz')},
    'tacker-base-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/networking-sfc/'
                     'networking-sfc-master.tar.gz')},
    'tempest': {
        'type': 'url',
        'location': ('$tarballs_base/tempest/'
                     'tempest-master.tar.gz')},
    'tripleo-ui': {
        'type': 'url',
        'location': ('$tarballs_base/tripleo-ui/'
                     'tripleo-ui-latest.tar.gz')},
    'trove-base': {
        'type': 'url',
        'location': ('$tarballs_base/trove/'
                     'trove-master.tar.gz')},
    'vitrage-base': {
        'type': 'url',
        'location': ('$tarballs_base/vitrage/'
                     'vitrage-master.tar.gz')},
    'vmtp': {
        'type': 'url',
        'location': ('$tarballs_base/vmtp/'
                     'vmtp-master.tar.gz')},
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/watcher/'
                     'watcher-master.tar.gz')},
    'zaqar': {
        'type': 'url',
        'location': ('$tarballs_base/zaqar/'
                     'zaqar-master.tar.gz')},
    'zun-base': {
        'type': 'url',
        'location': ('$tarballs_base/zun/'
                     'zun-master.tar.gz')}
}


# NOTE(SamYaple): Only increment the UID. Never reuse old or removed UIDs.
#     Starting point 42400+ was chosen arbitrarily to ensure no conflicts
USERS = {
    'kolla-user': {
        'uid': 42400,
        'gid': 42400,
    },
    'ansible-user': {
        'uid': 42401,
        'gid': 42401,
    },
    'aodh-user': {
        'uid': 42402,
        'gid': 42402,
    },
    'barbican-user': {
        'uid': 42403,
        'gid': 42403,
    },
    'bifrost-user': {
        'uid': 42404,
        'gid': 42404,
    },
    'ceilometer-user': {
        'uid': 42405,
        'gid': 42405,
    },
    'chrony-user': {
        'uid': 42406,
        'gid': 42406,
    },
    'cinder-user': {
        'uid': 42407,
        'gid': 42407,
    },
    'cloudkitty-user': {
        'uid': 42408,
        'gid': 42408,
    },
    'collectd-user': {
        'uid': 42409,
        'gid': 42409,
    },
    'congress-user': {
        'uid': 42410,
        'gid': 42410,
    },
    'designate-user': {
        'uid': 42411,
        'gid': 42411,
    },
    'elasticsearch-user': {
        'uid': 42412,
        'gid': 42412,
    },
    'etcd-user': {
        'uid': 42413,
        'gid': 42413,
    },
    'freezer-user': {
        'uid': 42414,
        'gid': 42414,
    },
    'glance-user': {
        'uid': 42415,
        'gid': 42415,
    },
    'gnocchi-user': {
        'uid': 42416,
        'gid': 42416,
    },
    'grafana-user': {
        'uid': 42417,
        'gid': 42417,
    },
    'heat-user': {
        'uid': 42418,
        'gid': 42418,
    },
    'horizon-user': {
        'uid': 42420,
        'gid': 42420,
    },
    'influxdb-user': {
        'uid': 42421,
        'gid': 42421,
    },
    'ironic-user': {
        'uid': 42422,
        'gid': 42422,
    },
    'kafka-user': {
        'uid': 42423,
        'gid': 42423,
    },
    'keystone-user': {
        'uid': 42425,
        'gid': 42425,
    },
    'kibana-user': {
        'uid': 42426,
        'gid': 42426,
    },
    'qemu-user': {
        'uid': 42427,
        'gid': 42427,
    },
    'magnum-user': {
        'uid': 42428,
        'gid': 42428,
    },
    'manila-user': {
        'uid': 42429,
        'gid': 42429,
    },
    'mistral-user': {
        'uid': 42430,
        'gid': 42430,
    },
    'monasca-user': {
        'uid': 42431,
        'gid': 42431,
    },
    'mongodb-user': {
        'uid': 42432,
        'gid': 65534,
    },
    'murano-user': {
        'uid': 42433,
        'gid': 42433,
    },
    'mysql-user': {
        'uid': 42434,
        'gid': 42434,
    },
    'neutron-user': {
        'uid': 42435,
        'gid': 42435,
    },
    'nova-user': {
        'uid': 42436,
        'gid': 42436,
    },
    'octavia-user': {
        'uid': 42437,
        'gid': 42437,
    },
    'panko-user': {
        'uid': 42438,
        'gid': 42438,
    },
    'rabbitmq-user': {
        'uid': 42439,
        'gid': 42439,
    },
    'rally-user': {
        'uid': 42440,
        'gid': 42440,
    },
    'sahara-user': {
        'uid': 42441,
        'gid': 42441,
    },
    'searchlight-user': {
        'uid': 42442,
        'gid': 42442,
    },
    'senlin-user': {
        'uid': 42443,
        'gid': 42443,
    },
    'solum-user': {
        'uid': 42444,
        'gid': 42444,
    },
    'swift-user': {
        'uid': 42445,
        'gid': 42445,
    },
    'tacker-user': {
        'uid': 42446,
        'gid': 42446,
    },
    'td-agent-user': {
        'uid': 42447,
        'gid': 42447,
    },
    'telegraf-user': {
        'uid': 42448,
        'gid': 42448,
    },
    'trove-user': {
        'uid': 42449,
        'gid': 42449,
    },
    'vmtp-user': {
        'uid': 42450,
        'gid': 42450,
    },
    'watcher-user': {
        'uid': 42451,
        'gid': 42451,
    },
    'zaqar-user': {
        'uid': 42452,
        'gid': 42452,
    },
    'zookeeper-user': {
        'uid': 42453,
        'gid': 42453,
    },
    'haproxy-user': {
        'uid': 42454,
        'gid': 42454,
    },
    'ceph-user': {
        'uid': 64045,
        'gid': 64045,
    },
    'memcached-user': {
        'uid': 42457,
        'gid': 42457,
    },
    'karbor-user': {
        'uid': 42458,
        'gid': 42458,
    },
    'vitrage-user': {
        'uid': 42459,
        'gid': 42459,
    },
    'redis-user': {
        'uid': 42460,
        'gid': 42460,
    },
    'ironic-inspector-user': {
        'uid': 42461,
        'gid': 42461,
    },
    'odl-user': {
        'uid': 42462,
        'gid': 42462,
    },
    'zun-user': {
        'uid': 42463,
        'gid': 42463,
    },
    'dragonflow-user': {
        'uid': 42464,
        'gid': 42464,
    },
    'qdrouterd-user': {
        'uid': 42465,
        'gid': 42465,
    },
    'ec2api-user': {
        'uid': 42466,
        'gid': 42466,
    },
    'sensu-user': {
        'uid': 42467,
        'gid': 42467,
    },
    'skydive-user': {
        'uid': 42468,
        'gid': 42468,
    },
    'kuryr-user': {
        'uid': 42469,
        'gid': 42469,
    },
    'novajoin-user': {
        'uid': 42470,
        'gid': 42470,
    },
    'blazar-user': {
        'uid': 42471,
        'gid': 42471,
    },
    'prometheus-user': {
        'uid': 42472,
        'gid': 42472,
    },
    'libvirt-user': {
        'uid': 42473,  # unused user, but we need the group for socket access
        'gid': 42473,
    },
    'fluentd-user': {
        'uid': 42474,
        'gid': 42474,
    },
    'almanach-user': {
        'uid': 42475,
        'gid': 42475,
    },
    'openvswitch-user': {
        'uid': 42476,  # unused user
        'gid': 42476,
    },
    'hugetlbfs-user': {
        'uid': 42477,  # unused user, but we need the group for vhost socket
        'gid': 42477,
    },
    'logstash-user': {
        'uid': 42478,
        'gid': 42478,
    },
    'storm-user': {
        'uid': 42479,
        'gid': 42479,
    },
    'tempest-user': {
        'uid': 42480,
        'gid': 42480,
    }
}


def get_source_opts(type_=None, location=None, reference=None):
    return [cfg.StrOpt('type', choices=['local', 'git', 'url'],
                       default=type_,
                       help='Source location type'),
            cfg.StrOpt('location', default=location,
                       help='The location for source install'),
            cfg.StrOpt('reference', default=reference,
                       help=('Git reference to pull, commit sha, tag '
                             'or branch name'))]


def get_user_opts(uid, gid):
    return [
        cfg.IntOpt('uid', default=uid, help='The user id'),
        cfg.IntOpt('gid', default=gid, help='The group id'),
    ]


def gen_all_user_opts():
    for name, params in USERS.items():
        uid = params['uid']
        gid = params['gid']
        yield name, get_user_opts(uid, gid)


def gen_all_source_opts():
    for name, params in SOURCES.items():
        type_ = params['type']
        location = params['location']
        reference = params.get('reference')
        yield name, get_source_opts(type_, location, reference)


def list_opts():
    return itertools.chain([(None, _CLI_OPTS),
                            (None, _BASE_OPTS),
                            ('profiles', _PROFILE_OPTS)],
                           gen_all_source_opts(),
                           gen_all_user_opts(),
                           )


def parse(conf, args, usage=None, prog=None,
          default_config_files=None):
    conf.register_cli_opts(_CLI_OPTS)
    conf.register_opts(_BASE_OPTS)
    conf.register_opts(_PROFILE_OPTS, group='profiles')
    for name, opts in gen_all_source_opts():
        conf.register_opts(opts, name)
    for name, opts in gen_all_user_opts():
        conf.register_opts(opts, name)

    conf(args=args,
         project='kolla',
         usage=usage,
         prog=prog,
         version=version.cached_version_string(),
         default_config_files=default_config_files)

    # NOTE(jeffrey4l): set the default base tag based on the
    # base option
    conf.set_default('base_tag', DEFAULT_BASE_TAGS.get(conf.base))

    if not conf.base_image:
        conf.base_image = conf.base
