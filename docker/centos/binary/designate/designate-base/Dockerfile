FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install designate-api because of /etc/designate/policy.json, which
# is needed in all services. This is probably a packaging bug. We do
# need the complete policy file because of some of the containers'
# requiring it. Remove the package when the file is moved though.
RUN yum install -y \
    MySQL-python \
    openstack-designate-api \
    openstack-designate-common \
    python-tooz \
    && yum clean all \
    && cp /etc/designate/policy.json /tmp/ \
    && rpm -e openstack-designate-api \
    && mv /tmp/policy.json /etc/designate/

COPY config-designate.sh /opt/kolla/config-designate.sh
