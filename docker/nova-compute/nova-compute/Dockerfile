FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Steven Dake <sdake@redhat.com>

# broken out by operation - we don't need libvirt and
# 200 deps for libguestfs (?)
RUN yum -y install curl
RUN yum -y install iscsi-initiator-utils
RUN yum -y install iptables
RUN yum -y install iptables-ipv6
RUN yum -y install ipmitool
RUN yum -y install libvirt-python
RUN yum -y install python-libguestfs
RUN yum -y install openssh-clients
RUN yum -y install rsync
RUN yum -y install lvm2
RUN yum -y install python-cinderclient
RUN yum -y install genisoimage
RUN yum -y install bridge-utils
RUN yum -y install openstack-nova-compute

ADD ./start.sh /start.sh
CMD ["/start.sh"]
