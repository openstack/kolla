FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-common \
     python-keystoneclient \
     python-cinderclient \
     python-nova \
     bridge-utils && yum clean all

ADD config-nova.sh /opt/kolla/config-nova.sh

