FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# TODO(inc0): when oslo_service lands in delorean, change pip to yum
# necessary until https://bugzilla.redhat.com/show_bug.cgi?id=1229477 is fixed
RUN yum -y install python-oslo-policy && yum clean all && pip install oslo.service

RUN mkdir -p /opt/kolla
COPY config-heat.sh /opt/kolla/config-heat.sh
