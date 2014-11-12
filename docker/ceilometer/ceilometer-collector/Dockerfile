FROM kollaglue/fedora-rdo-ceilometer-base
MAINTAINER Pradeep Kilambi <pkilambi@cisco.com>

RUN yum install -y openstack-ceilometer-collector && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
