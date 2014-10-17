FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Steven Dake <sdake@redhat.com>

RUN yum -y install openstack-nova-network \
        ; yum clean all

ADD ./start.sh /start.sh

VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]

CMD ["/start.sh"]
