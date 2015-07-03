FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openvswitch \
    && yum clean all

COPY config-internal.sh config-external.sh /opt/kolla/
