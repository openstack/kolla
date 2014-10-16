FROM kollaglue/fedora-rdo-nova-ctr-base
MAINTAINER Ryan Hallisey <rhallise@redhat.com>

RUN yum -y install \
        openstack-nova-api && yum clean all

EXPOSE 8773 8774 8775

ADD ./start.sh /start.sh
CMD ["/start.sh"]
