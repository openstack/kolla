FROM kollaglue/fedora-rdo-base
MAINTAINER Ryan Hallisey <rhallisey@redhat.com>

RUN yum -y install openstack-nova-common \
     python-keystoneclient \
     python-nova && yum clean all

ADD config-nova-controller.sh /opt/kolla/config-nova-controller.sh

