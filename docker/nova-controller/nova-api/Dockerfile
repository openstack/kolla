FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-api && yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
