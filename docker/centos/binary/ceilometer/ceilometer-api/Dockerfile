FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%ceilometer-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-ceilometer-api && yum clean all

COPY ./start.sh /start.sh
COPY config-internal.sh config-external.sh /opt/kolla/
CMD ["/start.sh"]
