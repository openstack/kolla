FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%glance-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

COPY config-internal.sh config-external.sh /opt/kolla/

ADD ./start.sh /start.sh
CMD ["/start.sh"]
