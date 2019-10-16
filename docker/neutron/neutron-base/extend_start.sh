#!/bin/bash

if [[ ! -d "/var/log/kolla/neutron" ]]; then
    mkdir -p /var/log/kolla/neutron
fi
if [[ $(stat -c %a /var/log/kolla/neutron) != "755" ]]; then
    chmod 755 /var/log/kolla/neutron
fi

# set legacy iptables to allow kernels not supporting iptables-nft
if /usr/bin/update-alternatives --query iptables; then
    if [[ $KOLLA_LEGACY_IPTABLES == "true" ]]; then
        sudo /usr/bin/update-alternatives --set iptables /usr/sbin/iptables-legacy
        sudo /usr/bin/update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
    else
        sudo /usr/bin/update-alternatives --auto iptables
        sudo /usr/bin/update-alternatives --auto ip6tables
    fi
fi

. /usr/local/bin/kolla_neutron_extend_start
