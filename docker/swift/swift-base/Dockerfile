FROM kollaglue/fedora-rdo-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-utils openstack-swift && yum clean all

# These will come after we sort out start time config
RUN mkdir /opt/swift
config-swift.sh /opt/swift/config-swift.sh
