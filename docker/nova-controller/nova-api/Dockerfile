FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-api && yum clean all

EXPOSE 8773 8774 8775

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
