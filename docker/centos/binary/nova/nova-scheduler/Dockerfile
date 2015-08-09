FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-scheduler && yum clean all

COPY start.sh /

COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
