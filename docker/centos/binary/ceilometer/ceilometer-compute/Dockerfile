FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%ceilometer-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-ceilometer-compute python-ceilometerclient python-pecan \
    && yum clean all

COPY ./start.sh /start.sh
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
