FROM centos
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Set up repositories
# This repository provides all dependencies used by RDO OpenStack
RUN yum install -y https://rdoproject.org/repos/openstack-kilo/rdo-release-kilo.rpm
# This repository provides latest packages built from trunk master into RPMs
RUN curl http://trunk.rdoproject.org/centos70/current/delorean.repo -o /etc/yum.repos.d/delorean-current.repo
# This repository provides crux which permits idempotent operation of RDO
RUN curl https://copr.fedoraproject.org/coprs/sdake/crux/repo/epel-7/sdake-crux-epel-7.repo -o /etc/yum.repos.d/sdake-crux-epel-7.repo

# Dependencies required for building/installing source components
RUN yum install -y \
    crux \
    crudini \
    gcc \
    git \
    libffi-devel \
    mariadb \
    MySQL-python \
    openssl \
    openssl-devel \
    python-devel \
    python-pip \
    tar \
    libxml2-devel \
    libxslt-devel \
  && yum clean all

RUN pip install --upgrade pip

RUN mkdir -p /opt/kolla
COPY service_hosts.sh kolla-common.sh /opt/kolla/
