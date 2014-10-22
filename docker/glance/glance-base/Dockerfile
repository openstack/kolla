FROM kollaglue/fedora-rdo-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-glance ; yum clean all

RUN mkdir -p /opt/kolla
COPY config-glance.sh /opt/kolla/config-glance.sh

