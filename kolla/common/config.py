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

from oslo_config import cfg
from oslo_config import types

from kolla.version import version_info as version


BASE_OS_DISTRO = ['centos', 'rhel', 'ubuntu', 'oraclelinux', 'debian']
DISTRO_RELEASE = {
    'centos': '7',
    'rhel': '7',
    'oraclelinux': '7',
    'debian': '8',
    'ubuntu': '16.04',
}
DELOREAN = ("http://buildlogs.centos.org/centos/7/cloud/x86_64/"
            "rdo-trunk-master-tested/delorean.repo")
# TODO(pbourke): update to buildlogs.centos.org once this moves
DELOREAN_DEPS = "http://trunk.rdoproject.org/centos7/delorean-deps.repo"
INSTALL_TYPE_CHOICES = ['binary', 'source', 'rdo', 'rhos']

TARBALLS_BASE = "http://tarballs.openstack.org"

_PROFILE_OPTS = [
    cfg.ListOpt('infra',
                default=[
                    'ceph',
                    'cron',
                    'elasticsearch',
                    'etcd',
                    'fluentd',
                    'haproxy',
                    'keepalived',
                    'kibana',
                    'kolla-toolbox',
                    'mariadb',
                    'memcached',
                    'mongodb',
                    'openvswitch',
                    'rabbitmq',
                    'redis',
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
                    'nova',
                    'swift',
                ],
                help='Main images'),
    cfg.ListOpt('aux',
                default=[
                    'aodh',
                    'cloudkitty',
                    'congress',
                    'designate',
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
                    'nova',
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
                    'nova',
                    'openvswitch',
                    'rabbitmq',
                ],
                help='Gate images')
]

_CLI_OPTS = [
    cfg.StrOpt('base', short='b', default='centos',
               choices=BASE_OS_DISTRO,
               help='The distro type of the base image. Allowed values '
                    'are ' + ', '.join(BASE_OS_DISTRO)),
    cfg.StrOpt('base-tag', default='latest',
               help='The base distro image tag'),
    cfg.StrOpt('base-image',
               help='The base image name. Default is the same with base'),
    cfg.BoolOpt('debug', short='d', default=False,
                help='Turn on debugging log level'),
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
    cfg.BoolOpt('cache', default=True,
                help='Use the Docker cache when building',
                ),
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
                     ' push properly.')),
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
               help=('Format to write the final results in')),
    cfg.StrOpt('tarballs-base', default=TARBALLS_BASE,
               help='Base url to OpenStack tarballs'),
    cfg.StrOpt('type', short='t', default='binary',
               choices=INSTALL_TYPE_CHOICES,
               dest='install_type',
               help=('The method of the OpenStack install. Allowed values '
                     'are ' + ', '.join(INSTALL_TYPE_CHOICES))),
    cfg.IntOpt('threads', short='T', default=8, min=1,
               help=('The number of threads to use while building.'
                     ' (Note: setting to one will allow real time'
                     ' logging.)')),
    cfg.StrOpt('tag', default=version.cached_version_string(),
               help='The Docker tag'),
    cfg.BoolOpt('template-only', default=False,
                help=("Don't build images. Generate Dockerfile only")),
    cfg.IntOpt('timeout', default=120,
               help='Time in seconds after which any operation times out'),
    cfg.MultiOpt('template-override', types.String(),
                 help='Path to template override file'),
    cfg.StrOpt('logs-dir', help='Path to logs directory'),
    cfg.BoolOpt('pull', default=True,
                help='Attempt to pull a newer version of the base image.'),
]

_BASE_OPTS = [
    cfg.StrOpt('maintainer',
               default='Kolla Project (https://launchpad.net/kolla)',
               help='The MAINTAINER field'),
    cfg.ListOpt('rpm_setup_config', default=[],
                help=('Comma separated list of .rpm or .repo file(s) '
                      'or URL(s) to install before building containers')),
    cfg.StrOpt('apt_sources_list', help=('Path to custom sources.list')),
    cfg.StrOpt('apt_preferences', help=('Path to custom apt/preferences'))
]


SOURCES = {
    'openstack-base': {
        'type': 'url',
        'location': ('$tarballs_base/requirements/'
                     'requirements-stable-ocata.tar.gz')},
    'aodh-base': {
        'type': 'url',
        'location': ('$tarballs_base/aodh/'
                     'aodh-4.0.0.tar.gz')},
    'barbican-base': {
        'type': 'url',
        'location': ('$tarballs_base/barbican/'
                     'barbican-4.0.0.tar.gz')},
    'bifrost-base': {
        'type': 'url',
        'location': ('$tarballs_base/bifrost/'
                     'bifrost-3.1.0.tar.gz')},
    'ceilometer-base': {
        'type': 'url',
        'location': ('$tarballs_base/ceilometer/'
                     'ceilometer-8.0.1.tar.gz')},
    'ceilometer-base-plugin-panko': {
        'type': 'url',
        'location': ('$tarballs_base/panko/'
                     'panko-2.0.2.tar.gz')},
    'cinder-base': {
        'type': 'url',
        'location': ('$tarballs_base/cinder/'
                     'cinder-10.0.2.tar.gz')},
    'congress-base': {
        'type': 'url',
        'location': ('$tarballs_base/congress/'
                     'congress-5.0.0.tar.gz')},
    'cloudkitty-base': {
        'type': 'url',
        'location': ('$tarballs_base/cloudkitty/'
                     'cloudkitty-5.0.1.tar.gz')},
    'designate-base': {
        'type': 'url',
        'location': ('$tarballs_base/designate/'
                     'designate-4.0.0.tar.gz')},
    'freezer-api': {
        'type': 'url',
        'location': ('$tarballs_base/freezer-api/'
                     'freezer-api-4.0.1.tar.gz')},
    'freezer-base': {
        'type': 'url',
        'location': ('$tarballs_base/freezer/'
                     'freezer-4.0.1.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('$tarballs_base/glance/'
                     'glance-14.0.0.tar.gz')},
    'gnocchi-base': {
        'type': 'url',
        'location': ('$tarballs_base/gnocchi/'
                     'gnocchi-3.1.2.tar.gz')},
    'heat-base': {
        'type': 'url',
        'location': ('$tarballs_base/heat/'
                     'heat-8.0.1.tar.gz')},
    'horizon': {
        'type': 'url',
        'location': ('$tarballs_base/horizon/'
                     'horizon-11.0.2.tar.gz')},
    'horizon-plugin-cloudkitty-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/cloudkitty-dashboard/'
                     'cloudkitty-dashboard-5.0.0.tar.gz')},
    'horizon-plugin-designate-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/designate-dashboard/'
                     'designate-dashboard-4.0.0.tar.gz')},
    'horizon-plugin-freezer-web-ui': {
        'type': 'url',
        'location': ('$tarballs_base/freezer-web-ui/'
                     'freezer-web-ui-4.0.1.tar.gz')},
    'horizon-plugin-ironic-ui': {
        'type': 'url',
        'location': ('$tarballs_base/ironic-ui/'
                     'ironic-ui-2.2.0.tar.gz')},
    'horizon-plugin-karbor-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/karbor-dashboard/'
                     'karbor-dashboard-0.1.2.tar.gz')},
    'horizon-plugin-magnum-ui': {
        'type': 'url',
        'location': ('$tarballs_base/magnum-ui/'
                     'magnum-ui-2.2.0.tar.gz')},
    'horizon-plugin-manila-ui': {
        'type': 'url',
        'location': ('$tarballs_base/manila-ui/'
                     'manila-ui-2.7.1.tar.gz')},
    'horizon-plugin-mistral-ui': {
        'type': 'url',
        'location': ('$tarballs_base/mistral-dashboard/'
                     'mistral-dashboard-4.0.0.tar.gz')},
    'horizon-plugin-monasca-ui': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-ui/'
                     'monasca-ui-1.5.0.tar.gz')},
    'horizon-plugin-murano-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/murano-dashboard/'
                     'murano-dashboard-3.2.0.tar.gz')},
    'horizon-plugin-neutron-lbaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-lbaas-dashboard/'
                     'neutron-lbaas-dashboard-2.0.0.tar.gz')},
    'horizon-plugin-sahara-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/sahara-dashboard/'
                     'sahara-dashboard-6.0.0.tar.gz')},
    'horizon-plugin-searchlight-ui': {
        'type': 'url',
        'location': ('$tarballs_base/searchlight-ui/'
                     'searchlight-ui-2.0.0.tar.gz')},
    'horizon-plugin-senlin-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/senlin-dashboard/'
                     'senlin-dashboard-0.6.0.tar.gz')},
    'horizon-plugin-solum-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/solum-dashboard/'
                     'solum-dashboard-2.0.0.tar.gz')},
    'horizon-plugin-tacker-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/tacker-horizon/'
                     'tacker-horizon-0.8.0.tar.gz')},
    'horizon-plugin-trove-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/trove-dashboard/'
                     'trove-dashboard-8.0.0.tar.gz')},
    'horizon-plugin-watcher-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/watcher-dashboard/'
                     'watcher-dashboard-1.0.0.tar.gz')},
    'horizon-plugin-zaqar-ui': {
        'type': 'url',
        'location': ('$tarballs_base/zaqar-ui/'
                     'zaqar-ui-2.0.0.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('$tarballs_base/ironic/'
                     'ironic-7.0.1.tar.gz')},
    'ironic-inspector': {
        'type': 'url',
        'location': ('$tarballs_base/ironic-inspector/'
                     'ironic-inspector-5.0.0.tar.gz')},
    'karbor-base': {
        'type': 'url',
        'location': ('$tarballs_base/karbor/'
                     'karbor-0.2.0.tar.gz')},
    'keystone-base': {
        'type': 'url',
        'location': ('$tarballs_base/keystone/'
                     'keystone-11.0.2.tar.gz')},
    'kuryr-base': {
        'type': 'url',
        'location': ('$tarballs_base/kuryr/'
                     'kuryr-lib-0.4.0.tar.gz')},
    'kuryr-libnetwork': {
        'type': 'url',
        'location': ('$tarballs_base/kuryr-libnetwork/'
                     'kuryr-libnetwork-0.1.0.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('$tarballs_base/magnum/'
                     'magnum-4.1.1.tar.gz')},
    'manila-base': {
        'type': 'url',
        'location': ('$tarballs_base/manila/'
                     'manila-4.0.0.tar.gz')},
    'mistral-base': {
        'type': 'url',
        'location': ('$tarballs_base/mistral/'
                     'mistral-4.0.2.tar.gz')},
    'monasca-api': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-api/'
                     'monasca-api-1.6.1.tar.gz')},
    'monasca-log-api': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-log-api/'
                     'monasca-log-api-1.4.1.tar.gz')},
    'monasca-notification': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-notification/'
                     'monasca-notification-1.7.0.tar.gz')},
    'monasca-persister': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-persister/'
                     'monasca-persister-1.4.0.tar.gz')},
    'monasca-statsd': {
        'type': 'url',
        'location': ('$tarballs_base/monasca-statsd/'
                     'monasca-statsd-1.5.0.tar.gz')},
    'murano-base': {
        'type': 'url',
        'location': ('$tarballs_base/murano/'
                     'murano-3.2.0.tar.gz')},
    'neutron-base': {
        'type': 'url',
        'location': ('$tarballs_base/neutron/'
                     'neutron-10.0.1.tar.gz')},
    'neutron-base-plugin-neutron-fwaas': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-fwaas/'
                     'neutron-fwaas-10.0.1.tar.gz')},
    'neutron-base-plugin-networking-generic-switch': {
        'type': 'url',
        'location': ('$tarballs_base/networking-generic-switch/'
                     'networking-generic-switch-stable-ocata.tar.gz')},
    'neutron-lbaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-lbaas/'
                     'neutron-lbaas-10.0.0.tar.gz')},
    'neutron-server-plugin-neutron-lbaas': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-lbaas/'
                     'neutron-lbaas-10.0.0.tar.gz')},
    'neutron-sfc-agent': {
        'type': 'url',
        'location': ('$tarballs_base/networking-sfc/'
                     'networking-sfc-4.0.0.tar.gz')},
    'neutron-server-plugin-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-vpnaas/'
                     'neutron-vpnaas-10.0.0.tar.gz')},
    'neutron-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/neutron-vpnaas/'
                     'neutron-vpnaas-10.0.0.tar.gz')},
    'nova-base': {
        'type': 'url',
        'location': ('$tarballs_base/nova/'
                     'nova-15.0.5.tar.gz')},
    'octavia-base': {
        'type': 'url',
        'location': ('$tarballs_base/octavia/'
                     'octavia-0.10.0.tar.gz')},
    'panko-base': {
        'type': 'url',
        'location': ('$tarballs_base/panko/'
                     'panko-2.0.2.tar.gz')},
    'rally': {
        'type': 'url',
        'location': ('$tarballs_base/rally/'
                     'rally-0.8.1.tar.gz')},
    'sahara-base': {
        'type': 'url',
        'location': ('$tarballs_base/sahara/'
                     'sahara-6.0.0.tar.gz')},
    'searchlight-base': {
        'type': 'url',
        'location': ('$tarballs_base/searchlight/'
                     'searchlight-2.0.0.tar.gz')},
    'senlin-base': {
        'type': 'url',
        'location': ('$tarballs_base/senlin/'
                     'senlin-3.0.1.tar.gz')},
    'solum-base': {
        'type': 'url',
        'location': ('$tarballs_base/solum/'
                     'solum-5.2.0.tar.gz')},
    'swift-base': {
        'type': 'url',
        'location': ('$tarballs_base/swift/'
                     'swift-2.13.0.tar.gz')},
    'tacker': {
        'type': 'url',
        'location': ('$tarballs_base/tacker/'
                     'tacker-0.7.0.tar.gz')},
    'tempest': {
        'type': 'url',
        'location': ('$tarballs_base/tempest/'
                     'tempest-15.0.0.tar.gz')},
    'trove-base': {
        'type': 'url',
        'location': ('$tarballs_base/trove/'
                     'trove-7.0.0.tar.gz')},
    'vitrage-base': {
        'type': 'url',
        'location': ('$tarballs_base/vitrage/'
                     'vitrage-1.5.1.tar.gz')},
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/watcher/'
                     'python-watcher-1.0.1.tar.gz')},
    'zaqar': {
        'type': 'url',
        'location': ('$tarballs_base/zaqar/'
                     'zaqar-4.0.0.tar.gz')},
    'zun-base': {
        'type': 'url',
        'location': ('$tarballs_base/zun/'
                     'zun-master.tar.gz')}
}


# NOTE(SamYaple): Only increment the UID. Never reuse old or removed UIDs.
#     Starting point 42400+ was choosen arbitrarily to ensure no conflicts
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
    'heka-user': {
        'uid': 42419,
        'gid': 42419,
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
        cfg.StrOpt('uid', default=uid, help='The user id'),
        cfg.StrOpt('gid', default=gid, help='The group id'),
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
    conf.set_default('base_tag', DISTRO_RELEASE.get(conf.base))

    if not conf.base_image:
        conf.base_image = conf.base
