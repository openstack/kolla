FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-cinder automaton && yum clean all

COPY config-cinder.sh /opt/kolla/config-cinder.sh

