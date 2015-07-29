FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Magnum is not yet in upstream RDO packaging

RUN curl https://copr.fedoraproject.org/coprs/sdake/openstack-magnum/repo/epel-7/sdake-openstack-magnum-epel-7.repo -o /etc/yum.repos.d/sdake-openstack-magnum-epel-7.repo

COPY config-magnum.sh /opt/kolla/
