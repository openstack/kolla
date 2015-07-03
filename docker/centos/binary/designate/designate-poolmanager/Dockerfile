FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%designate-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# The bind9 package here is only to provide the rndc binary.
RUN yum install -y \
    openstack-designate-pool-manager \
    bind \
    && yum clean all

COPY start.sh /start.sh
COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
