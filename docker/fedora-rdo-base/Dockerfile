FROM fedora:20
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Set up repositories
RUN yum install -y https://rdo.fedorapeople.org/rdo-release.rpm
RUN yum -y install dnf dnf-plugins-core; yum clean all
RUN dnf copr enable -y larsks/crux

# Update packages
RUN yum update -y; yum clean all

# Install base packages
RUN yum install -y \
	crux \
	mariadb \
	mariadb-libs \
	openssl \
	openstack-utils \
	pyparsing \
	python-alembic \
	python-amqp \
	python-amqplib \
	python-anyjson \
	python-boto \
	python-cheetah \
	python-cliff \
	python-cmd2 \
	python-croniter \
	python-crypto \
	python-d2to1 \
	python-docutils \
	python-dogpile-cache \
	python-dogpile-core \
	python-empy \
	python-eventlet \
	python-flask \
	python-futures \
	python-greenlet \
	python-httplib2 \
	python-iso8601 \
	python-itsdangerous \
	python-jinja2 \
	python-jsonpatch \
	python-jsonpath-rw \
	python-jsonpointer \
	python-jsonschema \
	python-keyring \
	python-kombu \
	python-ldap \
	python-lesscpy \
	python-lockfile \
	python-lxml \
	python-markdown \
	python-memcached \
	python-migrate \
	python-msgpack \
	python-netifaces \
	python-networkx \
	python-oauthlib \
	python-oslo-config \
	python-oslo-messaging \
	python-oslo-rootwrap \
	python-paramiko \
	python-passlib \
	python-paste-deploy \
	python-pbr \
	python-pecan \
	python-ply \
	python-prettytable \
	python-psutil \
	python-pycadf \
	python-pygments \
	python-pymongo \
	python-qpid \
	python-repoze-lru \
	python-requests \
	python-routes \
	python-simplegeneric \
	python-simplejson \
	python-singledispatch \
	python-six \
	python-sqlalchemy \
	python-stevedore \
	python-taskflow \
	python-versiontools \
	python-warlock \
	python-webob \
	python-websockify \
	python-webtest \
	python-werkzeug \
	python-wsme \
	; yum clean all

RUN mkdir -p /opt/kolla
ADD service_hosts.sh /opt/kolla/service_hosts.sh
ADD kolla-common.sh /opt/kolla/kolla-common.sh
