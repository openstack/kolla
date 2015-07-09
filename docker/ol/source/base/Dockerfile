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

# TODO(pbourke): replace pip and crux below with rpms once available in Oracle
# repos
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py

RUN pip install crudini

RUN curl https://codeload.github.com/larsks/crux/tar.gz/7 -o /crux-7.tar.gz \
    && tar -xf /crux-7.tar.gz \
    && pip install -r /crux-7/requirements.txt \
    && pip install /crux-7 \
    && rm -rf /crux-7.tar.gz /crux-7

COPY service_hosts.sh kolla-common.sh /opt/kolla/
