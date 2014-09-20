FROM fedora-rdo-base
MAINTAINER Steven Dake <sdake@redhat.com>

RUN yum -y install \
	openstack-utils \
	openstack-heat && yum clean all

# These will come after we sort out start time config
#RUN mkdir /opt/heat
#COPY config-heat.sh /opt/heat/config-heat.sh
