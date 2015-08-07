FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%designate-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y \
    openstack-designate-central \
    && yum clean all

COPY start.sh /start.sh
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
