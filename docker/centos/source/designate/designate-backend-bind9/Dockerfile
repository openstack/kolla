FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%designate-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

COPY start.sh /start.sh
COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
