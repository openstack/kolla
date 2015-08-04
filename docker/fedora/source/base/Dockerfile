FROM fedora:21
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# This repository provides crux which permits idempotent operation of RDO
RUN curl https://copr.fedoraproject.org/coprs/sdake/crux/repo/epel-7/sdake-crux-epel-7.repo -o \
    /etc/yum.repos.d/sdake-crux-epel-7.repo

# Dependencies required for building/installing source components
RUN yum install -y \
    crux \
    gcc \
    git \
    libffi-devel \
    libxml2-devel \
    libxslt-devel \
    mariadb \
    mariadb-devel \
    mysql-devel \
    MySQL-python \
    openldap-devel \
    openssl \
    openssl-devel \
    postgresql \
    postgresql-devel \
    python-devel \
    python-oslo-policy \
    sqlite-devel \
    tar \
  && yum clean all


# the only dependencies we need from RDO in the source builds are
# python-pip, python-cliff for crux, and crudini,
# all of which can be pulled from pypi.
# also the older version of pip does not have support for wheels
# we are installing from source pip is the important for
# most dependency installations
# https://bugs.launchpad.net/kolla/+bug/1476760
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py

RUN pip install --upgrade \
    cachetools \
    crudini \
    pip \
    tox

COPY kolla-common.sh /opt/kolla/
