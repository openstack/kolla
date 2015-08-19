FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-neutron \
                   openstack-neutron-ml2 \
                   openvswitch \
                   && yum clean all

# TODO (sdake): remove once RDO adds to the openstack-neutron package
RUN pip install oslo.versionedobjects

COPY config-sudoers.sh /opt/kolla/
