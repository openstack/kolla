FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-glance && yum clean all

RUN mkdir -p /opt/kolla
COPY config-glance.sh /opt/kolla/config-glance.sh

