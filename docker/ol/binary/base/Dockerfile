FROM oraclelinux:7.1
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum update -y \
    && yum install -y git \
    && yum clean all \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm -f get-pip.py \
    && pip install crudini

COPY service_hosts.sh kolla-common.sh /opt/kolla/
