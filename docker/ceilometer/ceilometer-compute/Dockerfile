FROM kollaglue/fedora-rdo-ceilometer-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-ceilometer-compute python-ceilometerclient python-pecan \
    && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
