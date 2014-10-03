FROM kollaglue/fedora-rdo-base
MAINTAINER Steven Dake <sdake@redhat.com>

RUN yum -y install libvirt \
        libvirt-daemon-kvm && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
