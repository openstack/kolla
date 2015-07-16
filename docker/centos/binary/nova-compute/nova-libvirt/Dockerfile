FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install libvirt-daemon \
        libguestfs \
        qemu-system-x86 \
        libvirt-daemon-driver-nwfilter \
        libvirt-daemon-config-nwfilter \
        libvirt-daemon-driver-lxc \
        && yum clean all

VOLUME [ "/sys/fs/cgroup" ]

COPY ./start.sh /start.sh

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
