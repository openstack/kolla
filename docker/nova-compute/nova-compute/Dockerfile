FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-nova-compute \
        sysfsutils ; yum clean all

ADD config-nova-compute.sh /opt/kolla/config-nova-compute.sh

ADD ./start.sh /start.sh

VOLUME [ "/sys/fs/cgroup" ]

CMD ["/start.sh"]
