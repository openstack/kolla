FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install supervisor
RUN easy_install supervisor

# Install supervisor-stdout
RUN pip install supervisor-stdout

# Install required packages
RUN yum install -y openstack-neutron-linuxbridge \
        net-tools \
        && yum clean all

# Add config scripts
ADD config-scripts/config-linuxbridge-agent.sh /opt/kolla/neutron/
ADD config-scripts/config-dhcp-agent.sh /opt/kolla/neutron/
ADD config-scripts/config-l3-agent.sh /opt/kolla/neutron/
ADD config-scripts/config-metadata-agent.sh /opt/kolla/neutron/
ADD config-scripts/config-sudoers.sh /opt/kolla/

# Add check scripts
ADD check-scripts/check-linuxbridge-agent.sh /opt/kolla/neutron/
ADD check-scripts/check-dhcp-agent.sh /opt/kolla/neutron/
ADD check-scripts/check-l3-agent.sh /opt/kolla/neutron/
ADD check-scripts/check-metadata-agent.sh /opt/kolla/neutron/

# Configure supervisord
RUN mkdir -p /var/log/supervisor/
ADD supervisord.conf /etc/

# Start supervisor
CMD ["/usr/bin/supervisord"]
