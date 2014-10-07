FROM kollaglue/fedora-rdo-nova-controller
MAINTAINER Ryan Hallisey <rhallise@redhat.com>

RUN yum -y install \
        openstack-nova-api && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
