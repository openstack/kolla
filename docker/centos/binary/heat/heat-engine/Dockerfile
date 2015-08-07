FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%heat-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    # until http://pkgs.fedoraproject.org/cgit/openstack-heat.git/tree/openstack-heat.spec#n248 \
    # is updated, the clients must remain here: \
    python-barbicanclient \
    python-zaqarclient \
    openstack-heat-engine \
    && yum clean all

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
