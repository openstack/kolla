FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%murano-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

COPY config-external.sh /opt/kolla/

COPY start.sh /

CMD ["/start.sh"]
