FROM kollaglue/fedora-rdo-heat-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-heat-engine \
    ; yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
