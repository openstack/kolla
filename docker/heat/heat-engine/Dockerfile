FROM kollaglue/fedora-rdo-heat-base
MAINTAINER Jeff Peeler <jpeeler@redhat.com>

RUN yum -y install \
    openstack-heat-engine \
    ; yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
