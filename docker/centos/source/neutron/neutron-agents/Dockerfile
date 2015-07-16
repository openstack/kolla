FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install supervisor
RUN easy_install supervisor

# Install supervisor-stdout
RUN pip install supervisor-stdout

# Configure supervisord
RUN mkdir -p /var/log/supervisor/
COPY supervisord.conf /etc/

# TODO: SamYaple FWaaS is part of the l3-agent, not a seperate agent that is
# why this file is needed. To support FWaaS we cannot have a seperate container
# I need to figure out the best way to make this work together
#
# This file _does_ _not_ need to exist, you must remove referencing it from the
# exec line in the start script. Also all these config options can exist in the
# main neutron.conf if we wish
COPY fwaas_driver.ini /etc/neutron/

COPY neutron-dhcp-agent/ /opt/kolla/neutron-dhcp-agent
COPY neutron-l3-agent/ /opt/kolla/neutron-l3-agent
COPY neutron-metadata-agent/ /opt/kolla/neutron-metadata-agent

CMD ["/usr/bin/supervisord"]
