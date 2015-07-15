FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-swift && yum clean all

COPY config-swift.sh build-swift-ring.py /opt/kolla/

RUN mkdir /opt/swift
