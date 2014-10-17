FROM kollaglue/fedora-rdo-nova-base
MAINTAINER Steven Dake <sdake@redhat.com>

# broken out by operation - we don't need libvirt and
# 200 deps for libguestfs (?)
RUN yum -y install curl \
	iscsi-initiator-utils \
	iptables \
	iptables-ipv6 \
	ipmitool \
	libvirt-python \
	python-libguestfs \
	openssh-clients \
	rsync \
	lvm2 \
	genisoimage \
	bridge-utils \
	openstack-nova-compute \
	; yum clean all

ADD config-nova-compute.sh /opt/kolla/config-nova-compute.sh
ADD ./start.sh /start.sh

CMD ["/start.sh"]
