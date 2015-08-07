FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

#Install required packages
RUN yum install -y which && \
    yum clean all

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
