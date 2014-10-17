FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Steven Dake <sdake@redhat.com>

RUN yum -y install openstack-nova-compute \
        libvirtd; yum clean all

ADD config-nova-compute.sh /opt/kolla/config-nova-compute.sh
ADD libvirt-start.sh /opt/kolla/libvirt-start.sh

ADD ./start.sh /start.sh

RUN mkdir -p /var/lib/libvirt/images/

VOLUME [ "/sys/fs/cgroup" ]
VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]

CMD ["/start.sh"]
