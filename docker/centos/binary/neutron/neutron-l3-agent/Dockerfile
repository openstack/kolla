FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# TODO: SamYaple FWaaS is part of the l3-agent, not a seperate agent that is
# why this file is needed. To support FWaaS we cannot have a seperate container
# I need to figure out the best way to make this work together
#
# This file _does_ _not_ need to exist, you must remove referencing it from the
# exec line in the start script. Also all these config options can exist in the
# main neutron.conf if we wish
COPY fwaas_driver.ini /etc/neutron/
COPY check.sh start.sh /

CMD ["/start.sh"]
