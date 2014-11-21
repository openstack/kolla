FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-network \
        bridge-utils && yum clean all

ADD config-nova-network.sh /opt/kolla/config-nova-network.sh
ADD ./start.sh /start.sh

VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]

CMD ["/start.sh"]
