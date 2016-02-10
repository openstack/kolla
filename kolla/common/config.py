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

from kolla import version


RDO_MIRROR = "http://trunk.rdoproject.org/centos7"
DELOREAN = "{}/current-passed-ci/delorean.repo".format(RDO_MIRROR)
DELOREAN_DEPS = "{}/delorean-deps.repo".format(RDO_MIRROR)
INSTALL_TYPE_CHOICES = ['binary', 'source', 'rdo', 'rhos']

_PROFILE_OPTS = [
    cfg.ListOpt('infra',
                default=['ceph', 'mariadb', 'haproxy',
                         'keepalived', 'kolla-toolbox', 'memcached',
                         'mongodb', 'openvswitch', 'rabbitmq', 'rsyslog'],
                help='Infra images'),
    cfg.ListOpt('main',
                default=['cinder', 'ceilometer', 'glance', 'heat',
                         'horizon', 'keystone', 'neutron', 'nova',
                         'swift'],
                help='Main images'),
    cfg.ListOpt('aux',
                default=['aodh', 'designate', 'gnocchi', 'ironic',
                         'magnum', 'mistral', 'trove,' 'zaqar', 'zookeeper'],
                help='Aux Images'),
    cfg.ListOpt('default',
                default=['kolla-toolbox', 'glance', 'haproxy',
                         'heat', 'horizon', 'keepalived', 'keystone',
                         'memcached', 'mariadb', 'neutron', 'nova',
                         'openvswitch', 'rabbitmq', 'rsyslog'],
                help='Default images'),
    cfg.ListOpt('gate',
                default=['ceph', 'cinder', 'glance', 'haproxy', 'heat',
                         'horizon', 'keepalived', 'keystone', 'kolla-toolbox',
                         'mariadb', 'memcached', 'neutron', 'nova',
                         'openvswitch', 'rabbitmq', 'rsyslog'],
                help='Gate images'),
    cfg.ListOpt('mesos',
                default=['chronos', 'marathon', 'mesos-master', 'mesos-slave',
                         'zookeeper'],
                help='Mesos images')
]

_CLI_OPTS = [
    cfg.StrOpt('base', short='b', default='centos',
               deprecated_group='kolla-build',
               help='The base distro to use when building'),
    cfg.StrOpt('base-tag', default='latest',
               deprecated_group='kolla-build',
               help='The base distro image tag'),
    cfg.BoolOpt('debug', short='d', default=False,
                deprecated_group='kolla-build',
                help='Turn on debugging log level'),
    cfg.DictOpt('build-args',
                help='Set docker build time variables'),
    cfg.StrOpt('include-header', short='i',
               deprecated_group='kolla-build',
               help=('Path to custom file to be added at '
                     'beginning of base Dockerfile')),
    cfg.StrOpt('include-footer', short='I',
               deprecated_group='kolla-build',
               help=('Path to custom file to be added at '
                     'end of Dockerfiles for final images')),
    cfg.BoolOpt('keep', default=False,
                deprecated_group='kolla-build',
                help='Keep failed intermediate containers'),
    cfg.StrOpt('namespace', short='n', default='kollaglue',
               deprecated_group='kolla-build',
               help='The Docker namespace name'),
    cfg.BoolOpt('cache', default=True,
                help='Use the Docker cache when building',
                ),
    cfg.BoolOpt('no-cache', default=False,
                help='Do not use the Docker cache when building',
                deprecated_for_removal=True),
    cfg.MultiOpt('profile', types.String(), short='p',
                 deprecated_group='kolla-build',
                 help=('Build a pre-defined set of images, see [profiles]'
                       ' section in config. The default profiles are:'
                       ' {}'.format(', '.join(
                           [opt.name for opt in _PROFILE_OPTS])
                       ))),
    cfg.BoolOpt('push', default=False,
                deprecated_group='kolla-build',
                help='Push images after building'),
    cfg.IntOpt('push-threads', default=1, min=1,
               deprecated_group='kolla-build',
               help=('The number of threads to user while pushing'
                     ' Images. Note: Docker can not handle threading'
                     ' push properly.')),
    cfg.IntOpt('retries', short='r', default=3, min=0,
               deprecated_group='kolla-build',
               help='The number of times to retry while building'),
    cfg.MultiOpt('regex', types.String(), positional=True,
                 help=('Build only images matching regex and its'
                       ' dependencies')),
    cfg.StrOpt('registry', deprecated_group='kolla-build',
               help=('The docker registry host. The default registry host'
                     ' is Docker Hub')),
    cfg.StrOpt('save-dependency',
               help=('Path to the file to store the docker image'
                     ' dependency in Graphviz dot format')),
    cfg.StrOpt('type', short='t', default='binary',
               choices=INSTALL_TYPE_CHOICES,
               dest='install_type', deprecated_group='kolla-build',
               help=('The method of the Openstack install. The valid'
                     ' types are: {}'.format(
                         ', '.join(INSTALL_TYPE_CHOICES)))),
    cfg.IntOpt('threads', short='T', default=8, min=1,
               deprecated_group='kolla-build',
               help=('The number of threads to use while building.'
                     ' (Note: setting to one will allow real time'
                     ' logging.)')),
    cfg.StrOpt('tag', default=version.version_info.cached_version_string(),
               deprecated_group='kolla-build',
               help='The Docker tag'),
    cfg.BoolOpt('template-only', default=False,
                deprecated_group='kolla-build',
                help=("Don't build images. Generate Dockerfile only")),
]

_BASE_OPTS = [
    cfg.StrOpt('maintainer', deprecated_group='kolla-build',
               default='Kolla Project (https://launchpad.net/kolla)',
               help='The MAINTAINER field'),
    cfg.ListOpt('rpm_setup_config', default=[DELOREAN, DELOREAN_DEPS],
                deprecated_group='kolla-build',
                help=('Comma separated list of .rpm or .repo file(s) '
                      'or URL(s) to install before building containers')),
    cfg.StrOpt('apt_sources_list', help=('Path to custom sources.list')),
    cfg.StrOpt('apt_preferences', help=('Path to custom apt/preferences'))
]


SOURCES = {
    'openstack-base': {
        'type': 'url',
        'location': ('https://github.com/openstack/requirements/tarball/'
                     'master')},
    'aodh-base': {
        'type': 'url',
        'location': 'http://tarballs.openstack.org/aodh/aodh-master.tar.gz'},
    'ceilometer-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/ceilometer/'
                     'ceilometer-master.tar.gz')},
    'cinder-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/cinder/'
                     'cinder-master.tar.gz')},
    'designate-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/designate/'
                     'designate-master.tar.gz')},
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
        'location': ('http://tarballs.openstack.org/heat/heat-master.tar.gz')},
    'horizon': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/horizon/'
                     'horizon-master.tar.gz')},
    'ironic-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/ironic/'
                     'ironic-master.tar.gz')},
    'keystone': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/keystone/'
                     'keystone-master.tar.gz')},
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
    'murano-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/murano/'
                     'murano-master.tar.gz')},
    'neutron-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/neutron/'
                     'neutron-master.tar.gz')},
    'nova-base': {
        'type': 'url',
        'location': 'http://tarballs.openstack.org/nova/nova-master.tar.gz'},
    'nova-spicehtml5proxy': {
        'type': 'url',
        'location': ('http://github.com/SPICE/spice-html5/tarball/'
                     'spice-html5-0.1.6')},
    'nova-novncproxy': {
        'type': 'url',
        'location': 'http://github.com/kanaka/noVNC/tarball/v0.5.1'},
    'swift-base': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/swift/'
                     'swift-master.tar.gz')},
    'tempest': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/tempest/'
                     'tempest-master.tar.gz')},
    'trove-base': {
        'type': 'url',
        'location': 'http://tarballs.openstack.org/trove/trove-master.tar.gz'},
    'zaqar': {
        'type': 'url',
        'location': ('http://tarballs.openstack.org/zaqar/'
                     'zaqar-master.tar.gz')}

}


def get_source_opts(type_=None, location=None, reference=None):
    return [cfg.StrOpt('type', choices=['git', 'url'],
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
         version=version.version_info.cached_version_string(),
         default_config_files=default_config_files)
