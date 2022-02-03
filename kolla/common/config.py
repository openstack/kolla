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


BASE_OS_DISTRO = ['centos', 'rhel', 'ubuntu', 'debian']
BASE_ARCH = ['x86_64', 'ppc64le', 'aarch64']
DEFAULT_BASE_TAGS = {
     'centos': {'name': 'quay.io/centos/centos', 'tag': 'stream8'},
     'rhel': {'name': 'registry.access.redhat.com/ubi8', 'tag': 'latest'},
     'debian': {'name': 'debian', 'tag': '10'},
     'ubuntu': {'name': 'ubuntu', 'tag': '20.04'},
}
DISTRO_RELEASE = {
    'centos': '8',
    'rhel': '8',
    'debian': '10',
    'ubuntu': '20.04',
}
OPENSTACK_RELEASE = 'victoria'

# This is noarch repository so we will use it on all architectures
DELOREAN = "https://trunk.rdoproject.org/centos8-master/" \
    "consistent/delorean.repo"
DELOREAN_DEPS = "https://trunk.rdoproject.org/centos8-master/" \
    "delorean-deps.repo"

INSTALL_TYPE_CHOICES = ['binary', 'source', 'rdo', 'rhos']

# TODO(mandre) check for file integrity instead of downloading from an HTTPS
# source
TARBALLS_BASE = "https://tarballs.opendev.org"

_PROFILE_OPTS = [
    cfg.ListOpt('infra',
                default=[
                    'certmonger',
                    'cron',
                    'elasticsearch',
                    'etcd',
                    'fluentd',
                    'haproxy',
                    'hacluster',
                    'keepalived',
                    'kibana',
                    'kolla-toolbox',
                    'logstash',
                    'mariadb',
                    'memcached',
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
                    'placement',
                    'swift',
                ],
                help='Main images'),
    cfg.ListOpt('aux',
                default=[
                    'aodh',
                    'blazar',
                    'cloudkitty',
                    'designate',
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
                    'masakari',
                    'mistral',
                    'monasca',
                    'murano',
                    'novajoin',
                    'octavia',
                    'panko',
                    'qinling',
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
                    'placement',
                    'openvswitch',
                    'rabbitmq',
                ],
                help='Default images'),
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
               help='The base architecture. Default is same as host.'),
    cfg.BoolOpt('use-dumb-init', default=True,
                help='Use dumb-init as init system in containers'),
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
               help=('The number of threads to use while pushing images.'
                     ' Note: Docker cannot handle threaded pushing properly')),
    cfg.IntOpt('retries', short='r', default=3, min=0,
               help='The number of times to retry while building'),
    cfg.MultiOpt('regex', types.String(), positional=True, required=False,
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
                 help=('Path to additional docker file template directory,'
                       ' can be specified multiple times'),
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
    cfg.StrOpt('openstack-release', default=OPENSTACK_RELEASE,
               help='OpenStack release for building kolla-toolbox'),
    cfg.StrOpt('openstack-branch', default='master',
               help='Branch for source images'),
    cfg.BoolOpt('docker-healthchecks', default=True,
                help='Add Kolla docker healthcheck scripts in the image'),
    cfg.BoolOpt('quiet', short='q', default=False,
                help='Do not print image logs'),
    cfg.BoolOpt('enable-unbuildable', default=False,
                help='Enable images marked as unbuildable'),
    cfg.BoolOpt('summary', default=True,
                help='Show summary at the end of build'),
    cfg.BoolOpt('infra-rename', default=False,
                help='Rename infrastructure images to infra')
]

_BASE_OPTS = [
    cfg.StrOpt('maintainer',
               default='Kolla Project (https://launchpad.net/kolla)',
               help='Content of the maintainer label'),
    cfg.StrOpt('distro_package_manager', default=None,
               help=('Use this parameter to override the default package '
                     'manager used by kolla. For example, if you want to use '
                     'yum on a system with dnf, set this to yum which will '
                     'use yum command in the build process')),
    cfg.StrOpt('base_package_type', default=None,
               help=('Set the package type of the distro. If not set then '
                     'the packaging type is set to "rpm" if a RHEL based '
                     'distro and "deb" if a Debian based distro.')),
    cfg.ListOpt('rpm_setup_config', default=[],
                help=('Comma separated list of .rpm or .repo file(s) '
                      'or URL(s) to install before building containers')),
    cfg.StrOpt('apt_sources_list', help=('Path to custom sources.list')),
    cfg.StrOpt('apt_preferences', help=('Path to custom apt/preferences')),
    cfg.BoolOpt('squash-cleanup', default=True,
                help='Remove source image from Docker after squashing'),
    cfg.StrOpt('squash-tmp-dir',
               help='Temporary directory to be used during squashing'),
    cfg.BoolOpt('clean_package_cache', default=True,
                help='Clean all package cache.')
]


SOURCES = {
    'openstack-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/requirements/'
                     'requirements-stable-victoria.tar.gz')},
    'aodh-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/aodh/'
                     'aodh-stable-victoria.tar.gz')},
    'barbican-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/barbican/'
                     'barbican-stable-victoria.tar.gz')},
    'bifrost-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/bifrost/'
                     'bifrost-stable-victoria.tar.gz')},
    'blazar-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar/'
                     'blazar-stable-victoria.tar.gz')},
    'ceilometer-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ceilometer/'
                     'ceilometer-stable-victoria.tar.gz')},
    'ceilometer-base-plugin-panko': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/panko/'
                     'panko-stable-victoria.tar.gz')},
    'cinder-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cinder/'
                     'cinder-stable-victoria.tar.gz')},
    'cloudkitty-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cloudkitty/'
                     'cloudkitty-stable-victoria.tar.gz')},
    'cyborg-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cyborg/'
                     'cyborg-stable-victoria.tar.gz')},
    'designate-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/designate/'
                     'designate-stable-victoria.tar.gz')},
    'ec2-api': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ec2-api/'
                     'ec2-api-stable-victoria.tar.gz')},
    'freezer-api': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/freezer-api/'
                     'freezer-api-stable-victoria.tar.gz')},
    'freezer-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/freezer/'
                     'freezer-stable-victoria.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/glance/'
                     'glance-stable-victoria.tar.gz')},
    'gnocchi-base': {
        'type': 'git',
        'reference': '4.3.4',
        'location': ('https://github.com/gnocchixyz/'
                     'gnocchi.git')},
    'heat-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/heat/'
                     'heat-stable-victoria.tar.gz')},
    'horizon': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/horizon/'
                     'horizon-stable-victoria.tar.gz')},
    'horizon-plugin-blazar-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar-dashboard/'
                     'blazar-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-cloudkitty-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cloudkitty-dashboard/'
                     'cloudkitty-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-designate-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/designate-dashboard/'
                     'designate-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-freezer-web-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/freezer-web-ui/'
                     'freezer-web-ui-stable-victoria.tar.gz')},
    'horizon-plugin-heat-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/heat-dashboard/'
                     'heat-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-ironic-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic-ui/'
                     'ironic-ui-stable-victoria.tar.gz')},
    'horizon-plugin-karbor-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/karbor-dashboard/'
                     'karbor-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-magnum-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum-ui/'
                     'magnum-ui-stable-victoria.tar.gz')},
    'horizon-plugin-manila-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/manila-ui/'
                     'manila-ui-stable-victoria.tar.gz')},
    'horizon-plugin-masakari-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/masakari-dashboard/'
                     'masakari-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-mistral-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/mistral-dashboard/'
                     'mistral-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-monasca-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-ui/'
                     'monasca-ui-stable-victoria.tar.gz')},
    'horizon-plugin-murano-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/murano-dashboard/'
                     'murano-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-neutron-vpnaas-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas-dashboard/'
                     'neutron-vpnaas-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-octavia-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/octavia-dashboard/'
                     'octavia-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-qinling-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/qinling-dashboard/'
                     'qinling-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-sahara-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-dashboard/'
                     'sahara-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-searchlight-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/searchlight-ui/'
                     'searchlight-ui-stable-victoria.tar.gz')},
    'horizon-plugin-senlin-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/senlin-dashboard/'
                     'senlin-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-solum-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/solum-dashboard/'
                     'solum-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-tacker-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tacker-horizon/'
                     'tacker-horizon-stable-victoria.tar.gz')},
    'horizon-plugin-trove-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/trove-dashboard/'
                     'trove-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-vitrage-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/vitrage-dashboard/'
                     'vitrage-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-watcher-dashboard': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher-dashboard/'
                     'watcher-dashboard-stable-victoria.tar.gz')},
    'horizon-plugin-zaqar-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zaqar-ui/'
                     'zaqar-ui-stable-victoria.tar.gz')},
    'horizon-plugin-zun-ui': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zun-ui/'
                     'zun-ui-stable-victoria.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic/'
                     'ironic-stable-victoria.tar.gz')},
    'ironic-inspector': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic-inspector/'
                     'ironic-inspector-stable-victoria.tar.gz')},
    'karbor-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/karbor/'
                     'karbor-stable-victoria.tar.gz')},
    'keystone-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/keystone/'
                     'keystone-stable-victoria.tar.gz')},
    'kuryr-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/kuryr/'
                     'kuryr-stable-victoria.tar.gz')},
    'kuryr-libnetwork': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/kuryr-libnetwork/'
                     'kuryr-libnetwork-stable-victoria.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum/'
                     'magnum-stable-victoria.tar.gz')},
    'manila-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/manila/'
                     'manila-stable-victoria.tar.gz')},
    'masakari-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/masakari/'
                     'masakari-stable-victoria.tar.gz')},
    'masakari-monitors': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/masakari-monitors/'
                     'masakari-monitors-stable-victoria.tar.gz')},
    'mistral-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/mistral/'
                     'mistral-stable-victoria.tar.gz')},
    'mistral-base-plugin-tacker': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tacker/'
                     'tacker-stable-victoria.tar.gz')},
    'monasca-agent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-agent/'
                     'monasca-agent-stable-victoria.tar.gz')},
    'monasca-api': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-api/'
                     'monasca-api-stable-victoria.tar.gz')},
    'monasca-notification': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-notification/'
                     'monasca-notification-stable-victoria.tar.gz')},
    'monasca-persister': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-persister/'
                     'monasca-persister-stable-victoria.tar.gz')},
    'monasca-statsd': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-statsd/'
                     'monasca-statsd-stable-victoria.tar.gz')},
    # FIXME(dszumski): Use openstack tar when infra is fixed
    'monasca-thresh': {
        'type': 'url',
        'location': ('https://github.com/openstack/monasca-thresh/archive/'
                     'stable/victoria.tar.gz')},
    'monasca-thresh-additions-monasca-common': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-common/'
                     'monasca-common-stable-victoria.tar.gz')},
    'murano-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/murano/'
                     'murano-stable-victoria.tar.gz')},
    'neutron-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron/'
                     'neutron-stable-victoria.tar.gz')},
    'neutron-base-plugin-networking-ansible': {
        'type': 'url',
        'location': ('$tarballs_base/x/networking-ansible/'
                     'networking-ansible-master.tar.gz')},
    'neutron-base-plugin-networking-baremetal': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-baremetal/'
                     'networking-baremetal-stable-victoria.tar.gz')},
    'neutron-base-plugin-networking-generic-switch': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-generic-switch/'
                     'networking-generic-switch-stable-victoria.tar.gz')},
    'neutron-base-plugin-networking-mlnx': {
        'type': 'url',
        'location': ('$tarballs_base/x/networking-mlnx/'
                     'networking-mlnx-stable-victoria.tar.gz')},
    'neutron-base-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-sfc/'
                     'networking-sfc-stable-victoria.tar.gz')},
    'neutron-base-plugin-vmware-nsx': {
        'type': 'url',
        'location': ('$tarballs_base/x/vmware-nsx/'
                     'vmware-nsx-master.tar.gz')},
    'neutron-base-plugin-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas/'
                     'neutron-vpnaas-stable-victoria.tar.gz')},
    'neutron-bgp-dragent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-dynamic-routing/'
                     'neutron-dynamic-routing-stable-victoria.tar.gz')},
    'neutron-server-plugin-neutron-dynamic-routing': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-dynamic-routing/'
                     'neutron-dynamic-routing-stable-victoria.tar.gz')},
    'neutron-server-plugin-vmware-nsxlib': {
        'type': 'url',
        'location': ('$tarballs_base/x/vmware-nsxlib/'
                     'vmware-nsxlib-master.tar.gz')},
    'neutron-vpnaas-agent': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-vpnaas/'
                     'neutron-vpnaas-stable-victoria.tar.gz')},
    'nova-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/nova/'
                     'nova-stable-victoria.tar.gz')},
    'nova-base-plugin-blazar': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar-nova/'
                     'blazar-nova-stable-victoria.tar.gz')},
    'nova-base-plugin-mksproxy': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/nova-mksproxy/'
                     'nova-mksproxy-0.0.2.tar.gz')},
    'novajoin-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/novajoin/'
                     'novajoin-1.3.0.tar.gz')},
    'octavia-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/octavia/'
                     'octavia-stable-victoria.tar.gz')},
    'octavia-api-plugin-ovn-octavia-provider': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ovn-octavia-provider/'
                     'ovn-octavia-provider-stable-victoria.tar.gz')},
    'octavia-driver-agent-plugin-ovn-octavia-provider': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ovn-octavia-provider/'
                     'ovn-octavia-provider-stable-victoria.tar.gz')},
    'panko-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/panko/'
                     'panko-stable-victoria.tar.gz')},
    'placement-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/placement/'
                     'placement-stable-victoria.tar.gz')},
    'qinling-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/qinling/'
                     'qinling-stable-victoria.tar.gz')},
    'tempest-plugin-tempest-conf': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/python-tempestconf/'
                     'python-tempestconf-master.tar.gz')},
    'tempest-plugin-barbican': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/barbican-tempest-plugin/'
                     'barbican_tempest_plugin-1.1.0.tar.gz')},
    'tempest-plugin-blazar': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/blazar-tempest-plugin/'
                     'blazar_tempest_plugin-0.5.0.tar.gz')},
    'tempest-plugin-cinder': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/cinder-tempest-plugin/'
                     'cinder-tempest-plugin-1.2.0.tar.gz')},
    'tempest-plugin-ec2api': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ec2api-tempest-plugin/'
                     'ec2api-tempest-plugin-1.1.0.tar.gz')},
    'tempest-plugin-heat': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/heat-tempest-plugin/'
                     'heat-tempest-plugin-1.1.0.tar.gz')},
    'tempest-plugin-ironic': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/ironic-tempest-plugin/'
                     'ironic-tempest-plugin-2.1.0.tar.gz')},
    'tempest-plugin-keystone': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/keystone-tempest-plugin/'
                     'keystone_tempest_plugin-0.5.0.tar.gz')},
    'tempest-plugin-magnum': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/magnum-tempest-plugin/'
                     'magnum_tempest_plugin-1.1.0.tar.gz')},
    'tempest-plugin-manila': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/manila-tempest-plugin/'
                     'manila-tempest-plugin-1.2.0.tar.gz')},
    'tempest-plugin-mistral': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/mistral-tempest-plugin/'
                     'mistral_tempest_tests-1.1.0.tar.gz')},
    'tempest-plugin-monasca': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/monasca-tempest-plugin/'
                     'monasca-tempest-plugin-2.1.0.tar.gz')},
    'tempest-plugin-murano': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/murano-tempest-plugin/'
                     'murano-tempest-plugin-2.1.0.tar.gz')},
    'tempest-plugin-neutron': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/neutron-tempest-plugin/'
                     'neutron-tempest-plugin-1.2.0.tar.gz')},
    'tempest-plugin-patrole': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/patrole/'
                     'patrole-0.10.0.tar.gz')},
    'tempest-plugin-telemetry': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/telemetry-tempest-plugin/'
                     'telemetry_tempest_plugin-1.1.0.tar.gz')},
    'tempest-plugin-trove': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/trove-tempest-plugin/'
                     'trove_tempest_plugin-1.1.0.tar.gz')},
    'tempest-plugin-vitrage': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/vitrage-tempest-plugin/'
                     'vitrage-tempest-plugin-5.1.0.tar.gz')},
    'tempest-plugin-watcher': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher-tempest-plugin/'
                     'watcher-tempest-plugin-2.1.0.tar.gz')},
    'tempest-plugin-zaqar': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zaqar-tempest-plugin/'
                     'zaqar_tempest_plugin-1.1.0.tar.gz')},
    'rally': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/rally/'
                     'rally-3.2.0.tar.gz')},
    'rally-plugin-openstack': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/rally-openstack/'
                     'rally-openstack-2.1.0.tar.gz')},
    'sahara-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara/'
                     'sahara-stable-victoria.tar.gz')},
    'sahara-base-plugin-ambari': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-ambari/'
                     'sahara-plugin-ambari-stable-victoria.tar.gz')},
    'sahara-base-plugin-cdh': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-cdh/'
                     'sahara-plugin-cdh-stable-victoria.tar.gz')},
    'sahara-base-plugin-mapr': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-mapr/'
                     'sahara-plugin-mapr-stable-victoria.tar.gz')},
    'sahara-base-plugin-spark': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-spark/'
                     'sahara-plugin-spark-stable-victoria.tar.gz')},
    'sahara-base-plugin-storm': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-storm/'
                     'sahara-plugin-storm-stable-victoria.tar.gz')},
    'sahara-base-plugin-vanilla': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/sahara-plugin-vanilla/'
                     'sahara-plugin-vanilla-stable-victoria.tar.gz')},
    'searchlight-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/searchlight/'
                     'searchlight-stable-victoria.tar.gz')},
    'senlin-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/senlin/'
                     'senlin-stable-victoria.tar.gz')},
    'solum-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/solum/'
                     'solum-stable-victoria.tar.gz')},
    'swift-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/swift/'
                     'swift-stable-victoria.tar.gz')},
    'tacker-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tacker/'
                     'tacker-stable-victoria.tar.gz')},
    'tacker-base-plugin-networking-sfc': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/networking-sfc/'
                     'networking-sfc-stable-victoria.tar.gz')},
    'tempest': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/tempest/'
                     'tempest-25.0.0.tar.gz')},
    'trove-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/trove/'
                     'trove-stable-victoria.tar.gz')},
    'vitrage-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/vitrage/'
                     'vitrage-stable-victoria.tar.gz')},
    'vmtp': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/vmtp/'
                     'vmtp-master.tar.gz')},
    'watcher-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/watcher/'
                     'watcher-stable-victoria.tar.gz')},
    'zaqar-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zaqar/'
                     'zaqar-stable-victoria.tar.gz')},
    'zun-base': {
        'type': 'url',
        'location': ('$tarballs_base/openstack/zun/'
                     'zun-stable-victoria.tar.gz')}
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
    'congress-user': {  # unused user (congress dropped)
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
    'mongodb-user': {  # unused user (mongodb dropped)
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
    'dragonflow-user': {  # unused user (dragonflow dropped)
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
    'sensu-user': {  # unused used (sensu dropped)
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
    'almanach-user': {  # unused user (almanach dropped)
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
    },
    'nfast-user': {
        'uid': 42481,  # unused user, but we need the group for thales hsm
        'gid': 42481,
    },
    'placement-user': {
        'uid': 42482,
        'gid': 42482,
    },
    'cyborg-user': {
        'uid': 42483,
        'gid': 42483,
    },
    'qinling-user': {
        'uid': 42484,
        'gid': 42484,
    },
    'masakari-user': {
        'uid': 42485,
        'gid': 42485,
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
    conf.set_default('base_tag', DEFAULT_BASE_TAGS[conf.base]['tag'])
    prefix = '' if conf.openstack_release == 'master' else 'stable-'
    openstack_branch = '{}{}'.format(prefix, conf.openstack_release)
    conf.set_default('openstack_branch', openstack_branch)

    if not conf.base_image:
        conf.base_image = DEFAULT_BASE_TAGS[conf.base]['name']
