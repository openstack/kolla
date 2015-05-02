FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# We really shouldn't need to install python-oslo-log or python-oslo-policy
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1218349
RUN yum -y install openstack-glance python-oslo-log python-oslo-policy && yum clean all

RUN mkdir -p /opt/kolla
COPY config-glance.sh /opt/kolla/config-glance.sh

