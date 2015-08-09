FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%magnum-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-magnum-api \
    && yum clean all

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
