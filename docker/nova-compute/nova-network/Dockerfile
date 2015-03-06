FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-network \
        bridge-utils initscripts && yum clean all

ADD config-nova-network.sh /opt/kolla/config-nova-network.sh
ADD ./start.sh /start.sh

VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]

CMD ["/start.sh"]
