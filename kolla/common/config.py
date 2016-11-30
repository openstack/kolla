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

_PROFILE_OPTS = [
    cfg.ListOpt('infra',
                default=['ceph', 'cron', 'elasticsearch', 'etcd', 'haproxy',
                         'heka', 'keepalived', 'kibana', 'kolla-toolbox',
                         'mariadb', 'memcached', 'mongodb', 'openvswitch',
                         'rabbitmq', 'tgtd'],
                help='Infra images'),
    cfg.ListOpt('main',
                default=['cinder', 'ceilometer', 'glance', 'heat',
                         'horizon', 'iscsi', 'keystone', 'neutron', 'nova',
                         'swift'],
                help='Main images'),
    cfg.ListOpt('aux',
                default=['aodh', 'cloudkitty', 'congress', 'designate',
                         'freezer', 'gnocchi', 'influxdb', 'ironic', 'kafka',
                         'karbor', 'kuryr', 'magnum', 'manila', 'mistral',
                         'monasca', 'murano', 'octavia', 'panko', 'rally',
                         'sahara', 'searchlight', 'senlin', 'solum', 'tacker',
                         'telegraf', 'trove', 'zaqar', 'zookeeper'],
                help='Aux Images'),
    cfg.ListOpt('default',
                default=['chrony', 'cron', 'kolla-toolbox', 'glance',
                         'haproxy', 'heat', 'horizon', 'keepalived',
                         'keystone', 'memcached', 'mariadb', 'neutron', 'nova',
                         'openvswitch', 'rabbitmq', 'heka'],
                help='Default images'),
    cfg.ListOpt('gate',
                default=['chrony', 'cron', 'glance', 'haproxy', 'keepalived',
                         'keystone', 'kolla-toolbox', 'mariadb', 'memcached',
                         'neutron', 'nova', 'openvswitch', 'rabbitmq', 'heka'],
                help='Gate images')
]

_CLI_OPTS = [
    cfg.StrOpt('base', short='b', default='centos',
               choices=BASE_OS_DISTRO,
               help='The distro type of the base image'),
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
                help='Show all available images'),
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
    cfg.StrOpt('type', short='t', default='binary',
               choices=INSTALL_TYPE_CHOICES,
               dest='install_type',
               help=('The method of the OpenStack install')),
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
    cfg.StrOpt('template-override',
               help='Path to template override file'),
    cfg.StrOpt('logs-dir', help='Path to logs directory'),
]

_BASE_OPTS = [
    cfg.StrOpt('maintainer',
               default='Kolla Project (https://launchpad.net/kolla)',
               help='The MAINTAINER field'),
    cfg.ListOpt('rpm_setup_config', default=[DELOREAN, DELOREAN_DEPS],
                help=('Comma separated list of .rpm or .repo file(s) '
                      'or URL(s) to install before building containers')),
    cfg.StrOpt('apt_sources_list', help=('Path to custom sources.list')),
    cfg.StrOpt('apt_preferences', help=('Path to custom apt/preferences'))
]


SOURCES = {
    'openstack-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/requirements/'
                     'requirements-master.tar.gz')},
    'aodh-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/aodh/'
                     'aodh-master.tar.gz')},
    'barbican-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/barbican/'
                     'barbican-master.tar.gz')},
    'bifrost-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/bifrost/'
                     'bifrost-master.tar.gz')},
    'ceilometer-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/ceilometer/'
                     'ceilometer-master.tar.gz')},
    'cinder-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/cinder/'
                     'cinder-master.tar.gz')},
    'congress-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/congress/'
                     'congress-master.tar.gz')},
    'cloudkitty-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/cloudkitty/'
                     'cloudkitty-master.tar.gz')},
    'designate-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/designate/'
                     'designate-master.tar.gz')},
    'freezer-api': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/freezer-api/'
                     'freezer-api-master.tar.gz')},
    'freezer-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/freezer/'
                     'freezer-master.tar.gz')},
    'glance-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/glance/'
                     'glance-master.tar.gz')},
    'gnocchi-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/gnocchi/'
                     'gnocchi-master.tar.gz')},
    'heat-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/heat/'
                     'heat-master.tar.gz')},
    'horizon': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/horizon/'
                     'horizon-master.tar.gz')},
    'horizon-plugin-cloudkitty-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/cloudkitty-dashboard/'
                     'cloudkitty-dashboard-master.tar.gz')},
    'horizon-plugin-designate-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/designate-dashboard/'
                     'designate-dashboard-master.tar.gz')},
    'horizon-plugin-ironic-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/ironic-ui/'
                     'ironic-ui-master.tar.gz')},
    'horizon-plugin-magnum-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/magnum-ui/'
                     'magnum-ui-master.tar.gz')},
    'horizon-plugin-manila-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/manila-ui/'
                     'manila-ui-master.tar.gz')},
    'horizon-plugin-mistral-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/mistral-dashboard/'
                     'mistral-dashboard-master.tar.gz')},
    'horizon-plugin-monasca-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/monasca-ui/'
                     'monasca-ui-1.2.1.tar.gz')},
    'horizon-plugin-neutron-lbaas-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron-lbaas-dashboard/'
                     'neutron-lbaas-dashboard-master.tar.gz')},
    'horizon-plugin-sahara-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/sahara-dashboard/'
                     'sahara-dashboard-master.tar.gz')},
    'horizon-plugin-searchlight-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/searchlight-ui/'
                     'searchlight-ui-master.tar.gz')},
    'horizon-plugin-senlin-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/senlin-dashboard/'
                     'senlin-dashboard-master.tar.gz')},
    'horizon-plugin-trove-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/trove-dashboard/'
                     'trove-dashboard-master.tar.gz')},
    'horizon-plugin-watcher-dashboard': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/watcher-dashboard/'
                     'watcher-dashboard-master.tar.gz')},
    'horizon-plugin-zaqar-ui': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/zaqar-ui/'
                     'zaqar-ui-master.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/ironic/'
                     'ironic-master.tar.gz')},
    'ironic-inspector': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/ironic-inspector/'
                     'ironic-inspector-master.tar.gz')},
    'kafka': {
        'type': 'url',
        'location': ('http://apache.osuosl.org/kafka/0.10.1.0/'
                     'kafka_2.11-0.10.1.0.tgz')},
    'karbor-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/karbor/'
                     'karbor-master.tar.gz')},
    'keystone-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/keystone/'
                     'keystone-master.tar.gz')},
    'kuryr-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/kuryr/'
                     'kuryr-master.tar.gz')},
    'kuryr-libnetwork': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/kuryr-libnetwork/'
                     'kuryr-libnetwork-master.tar.gz')},
    'magnum-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/magnum/'
                     'magnum-master.tar.gz')},
    'manila-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/manila/'
                     'manila-master.tar.gz')},
    'mistral-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/mistral/'
                     'mistral-master.tar.gz')},
    'monasca-api': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/monasca-api/'
                     'monasca-api-1.3.1.tar.gz')},
    'monasca-log-api': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/monasca-log-api/'
                     'monasca-log-api-1.1.0.tar.gz')},
    'monasca-notification': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/monasca-notification/'
                     'monasca-notification-1.4.0.tar.gz')},
    'monasca-persister': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/monasca-persister/'
                     'monasca-persister-1.1.0.tar.gz')},
    'monasca-statsd': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/monasca-statsd/'
                     'monasca-statsd-1.3.0.tar.gz')},
    'murano-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/murano/'
                     'murano-master.tar.gz')},
    'neutron-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron/'
                     'neutron-master.tar.gz')},
    'neutron-base-plugin-neutron-fwaas': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron-fwaas/'
                     'neutron-fwaas-master.tar.gz')},
    'neutron-lbaas-agent': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron-lbaas/'
                     'neutron-lbaas-master.tar.gz')},
    'neutron-server-plugin-neutron-lbaas': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron-lbaas/'
                     'neutron-lbaas-master.tar.gz')},
    'neutron-sfc-agent': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/networking-sfc/'
                     'networking-sfc-master.tar.gz')},
    'neutron-server-plugin-vpnaas-agent': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron-vpnaas/'
                     'neutron-vpnaas-master.tar.gz')},
    'neutron-vpnaas-agent': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron-vpnaas/'
                     'neutron-vpnaas-master.tar.gz')},
    'nova-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/nova/'
                     'nova-master.tar.gz')},
    'nova-spicehtml5proxy': {
        'type': 'url',
        'location': ('http://github.com/SPICE/spice-html5/tarball/'
                     'spice-html5-0.1.6')},
    'nova-novncproxy': {
        'type': 'url',
        'location': ('http://github.com/kanaka/noVNC/tarball/'
                     'v0.5.1')},
    'octavia-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/octavia/'
                     'octavia-master.tar.gz')},
    'panko-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/panko/'
                     'panko-master.tar.gz')},
    'rally': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/rally/'
                     'rally-master.tar.gz')},
    'sahara-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/sahara/'
                     'sahara-master.tar.gz')},
    'searchlight-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/searchlight/'
                     'searchlight-master.tar.gz')},
    'senlin-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/senlin/'
                     'senlin-master.tar.gz')},
    'solum-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/solum/'
                     'solum-master.tar.gz')},
    'swift-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/swift/'
                     'swift-master.tar.gz')},
    'tacker': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/tacker/'
                     'tacker-master.tar.gz')},
    'tempest': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/tempest/'
                     'tempest-master.tar.gz')},
    'trove-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/trove/'
                     'trove-master.tar.gz')},
    'watcher-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/watcher/'
                     'watcher-master.tar.gz')},
    'zaqar': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/zaqar/'
                     'zaqar-master.tar.gz')}
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
                           )


def parse(conf, args, usage=None, prog=None,
          default_config_files=None):
    conf.register_cli_opts(_CLI_OPTS)
    conf.register_opts(_BASE_OPTS)
    conf.register_opts(_PROFILE_OPTS, group='profiles')
    for name, opts in gen_all_source_opts():
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
