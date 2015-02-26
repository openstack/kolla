FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-dashboard && yum clean all

EXPOSE 80

ADD ./start.sh /start.sh

CMD ["/start.sh"]
