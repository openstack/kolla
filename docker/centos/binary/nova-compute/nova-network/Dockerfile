FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-network \
        bridge-utils initscripts && yum clean all

COPY config-nova-network.sh /opt/kolla/config-nova-network.sh
COPY ./start.sh /start.sh

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
