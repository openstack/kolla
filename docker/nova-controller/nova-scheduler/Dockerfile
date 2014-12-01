FROM kollaglue/fedora-rdo-nova-base:l3_ovs_wip
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-scheduler && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
