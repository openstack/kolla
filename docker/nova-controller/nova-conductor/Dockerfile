FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-conductor && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
