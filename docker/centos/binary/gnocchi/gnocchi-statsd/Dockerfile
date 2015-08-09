FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%gnocchi-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-gnocchi-statsd && yum clean all

COPY start.sh /

CMD ["/start.sh"]
