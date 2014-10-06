FROM kollaglue/fedora-rdo-base
MAINTAINER Ryan Hallisey <rhallisey@redhat.com>

RUN yum -y install openstack-nova-common \
    install python-keystoneclient \
    install python-nova \
    install python-oslo-messaging \
    install python-websockify && yum clean all
