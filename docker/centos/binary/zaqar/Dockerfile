FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-zaqar && yum clean all

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
