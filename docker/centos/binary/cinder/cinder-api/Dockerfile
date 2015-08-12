FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%cinder-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y python-keystone && yum clean all
COPY config-external.sh /opt/kolla/
COPY ./start.sh ./check.sh /

CMD ["/start.sh"]
