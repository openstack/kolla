FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%swift-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-swift-object \
    && yum clean all

COPY config-swift-object.sh /opt/kolla/
