FROM kollaglue/fedora-rdo-base
MAINTAINER Ryan Hallisey <rhallisey@redhat.com>

RUN yum -y install openstack-nova-common \
     python-keystoneclient \
     python-nova && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
