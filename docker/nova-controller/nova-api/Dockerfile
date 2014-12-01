FROM kollaglue/fedora-rdo-nova-base:l3_ovs_wip
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-api && yum clean all

EXPOSE 8773 8774 8775

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
