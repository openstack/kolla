FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        hostname \
        keepalived \
        socat \
    && yum clean all

COPY start.sh check_alive.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
