FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%heat-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-heat-api-cfn \
    python-openstackclient \
    && yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
