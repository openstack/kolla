#!/bin/bash

if [[ ! -d "/var/log/kolla/ironic" ]]; then
    mkdir -p /var/log/kolla/ironic
fi
if [[ $(stat -c %a /var/log/kolla/ironic) != "755" ]]; then
    chmod 755 /var/log/kolla/ironic
fi
if [[ ! -r "/var/log/kolla/ironic/dnsmasq.log" ]]; then
    touch /var/log/kolla/ironic/dnsmasq.log
    chown ironic:ironic /var/log/kolla/ironic/dnsmasq.log
fi
