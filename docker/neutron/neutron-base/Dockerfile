FROM kollaglue/fedora-rdo-base:l3_ovs_wip
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-neutron-ml2 ; yum clean all

RUN mkdir -p /opt/kolla
COPY config-neutron.sh /opt/kolla/config-neutron.sh

