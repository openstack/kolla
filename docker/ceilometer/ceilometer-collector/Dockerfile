FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%ceilometer-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-ceilometer-collector && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
