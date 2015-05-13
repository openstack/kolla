FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%heat-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-heat-engine \
    && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
