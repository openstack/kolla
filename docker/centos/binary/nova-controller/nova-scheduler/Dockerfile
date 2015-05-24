FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        openstack-nova-scheduler && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]
