FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Ryan Hallisey <rhallise@redhat.com>

RUN yum -y install \
        openstack-nova-scheduler && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
