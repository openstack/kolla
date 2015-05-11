FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%magnum-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-magnum-api \
    && yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
