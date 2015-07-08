FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-neutron \
                   openstack-neutron-ml2 \
                   python-neutron-client \
                   && yum clean all

COPY config-neutron.sh config-sudoers.sh /opt/kolla/
