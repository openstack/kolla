FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-network \
        bridge-utils && yum clean all

ADD ./start.sh /start.sh

VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]

CMD ["/start.sh"]
