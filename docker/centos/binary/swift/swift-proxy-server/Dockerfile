FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%swift-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-swift-proxy && yum clean all

COPY ./start.sh /start.sh

COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
