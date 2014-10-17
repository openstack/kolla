FROM kollaglue/fedora-rdo-base
MAINTAINER Ryan Hallisey <rhallisey@redhat.com>

RUN yum -y install openstack-nova-common \
     python-keystoneclient \
     python-cinderclient \
     python-nova \
     bridge-utils && yum clean all

ADD config-nova.sh /opt/kolla/config-nova.sh

