FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%cinder-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y python-keystone && yum clean all

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
