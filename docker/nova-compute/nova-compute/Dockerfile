FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-compute sysfsutils \
        libvirt-daemon-config-nwfilter ; yum clean all

ADD config-nova-compute.sh /opt/kolla/config-nova-compute.sh

ADD ./start.sh /start.sh

VOLUME [ "/sys/fs/cgroup" ]
VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]

CMD ["/start.sh"]
