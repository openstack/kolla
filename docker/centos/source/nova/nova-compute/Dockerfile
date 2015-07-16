FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install sysfsutils && yum clean all

COPY ./start.sh /start.sh

COPY config-nova-compute.sh config-internal.sh config-external.sh /opt/kolla/

VOLUME [ "/sys/fs/cgroup" ]

CMD ["/start.sh"]
