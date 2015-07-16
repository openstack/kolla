FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install required packages
RUN yum install -y \
        https://rdoproject.org/repos/openstack-kilo/rdo-release-kilo.rpm \
        openvswitch \
    && yum clean all

COPY check.sh start.sh /

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
