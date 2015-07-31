FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%swift-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-swift-container \
    && yum clean all

COPY start.sh /
COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
