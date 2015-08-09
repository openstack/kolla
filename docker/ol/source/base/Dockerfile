FROM oraclelinux:7.1
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Dependencies required for building/installing source components
RUN yum install -y \
    MySQL-python \
    gcc \
    git \
    libffi-devel \
    mariadb \
    openssl \
    openssl-devel \
    python-devel \
    tar \
  && yum clean all

# TODO(pbourke): replace pip below with rpms once available in Oracle
# repos
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py

RUN pip install crudini

COPY kolla-common.sh /opt/kolla/
