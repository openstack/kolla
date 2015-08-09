FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%ovs-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

COPY start.sh /
COPY ovs_ensure_configured.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
