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
        openssl \
    && apt-get clean

COPY service_hosts.sh kolla-common.sh /opt/kolla/
