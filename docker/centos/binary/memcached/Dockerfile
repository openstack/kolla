FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install memcached && yum clean all

COPY start.sh /

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
