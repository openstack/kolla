FROM ubuntu:trusty
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN apt-get update \
    && apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository cloud-archive:kilo \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get dist-upgrade -y \
    && apt-get install -y --no-install-recommends \
        crudini \
        curl \
        gcc \
        ldap-utils \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        mysql-server\
        openssl \
        postgresql \
        python-dev \
        python-oslo-policy \
        slapd \
        sqlite \
        tar \
    && apt-get clean

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
