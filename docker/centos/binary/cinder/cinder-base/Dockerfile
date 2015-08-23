FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-cinder \
        python-automaton \
    && sed -i "s|udev_rules = 1|udev_rules = 0|g" /etc/lvm/lvm.conf \
    && sed -i "s|udev_sync = 1|udev_sync = 0|g" /etc/lvm/lvm.conf \
    && yum clean all

# NOTE(sdake): The sed operations make LVM tools work inside a container - see
# https://groups.google.com/forum/#!topic/docker-user/n4Xtvsb4RAw
