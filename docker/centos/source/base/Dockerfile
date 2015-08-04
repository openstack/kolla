FROM centos
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Dependencies required for building/installing source components
RUN yum install -y \
    epel-release \
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

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py

RUN pip install --upgrade \
    cachetools \
    crudini \
    crux \
    pip \
    tox

COPY kolla-common.sh /opt/kolla/
