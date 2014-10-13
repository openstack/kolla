FROM kollaglue/fedora-rdo-base
MAINTAINER Dan Radez <dradez@redhat.com>

RUN yum -y install openstack-glance ; yum clean all

RUN mkdir -p /opt/kolla
COPY config-glance.sh /opt/kolla/config-glance.sh

