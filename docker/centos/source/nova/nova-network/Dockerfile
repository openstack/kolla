FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install initscripts && yum clean all

COPY ./start.sh /start.sh

COPY config-nova-network.sh config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
