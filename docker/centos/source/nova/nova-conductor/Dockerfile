FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./start.sh /start.sh

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
