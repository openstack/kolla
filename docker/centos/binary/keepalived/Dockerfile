FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        hostname \
        keepalived \
        socat \
    && yum clean all

COPY keepalived.conf /etc/keepalived/
COPY start.sh check_alive.sh /
COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
