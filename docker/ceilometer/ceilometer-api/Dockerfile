FROM kollaglue/fedora-rdo-ceilometer-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-ceilometer-api && yum clean all

EXPOSE 8777

ADD ./start.sh /start.sh
CMD ["/start.sh"]
