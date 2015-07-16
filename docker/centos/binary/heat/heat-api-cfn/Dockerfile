FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%heat-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-heat-api-cfn \
    python-openstackclient \
    && yum clean all

COPY ./start.sh /start.sh
COPY ./check.sh /check.sh

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
