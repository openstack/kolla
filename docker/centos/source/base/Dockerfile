FROM centos
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Dependencies required for building/installing source components
RUN yum install -y \
    gcc \
    git \
    libffi-devel \
    mariadb \
    MySQL-python \
    openssl \
    openssl-devel \
    python-devel \
    tar \
    libxml2-devel \
    libxslt-devel \
  && yum clean all

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py

RUN pip install --upgrade \
    crudini \
    crux \
    pip

RUN mkdir -p /opt/kolla
COPY service_hosts.sh kolla-common.sh /opt/kolla/
