#!/bin/bash

if [[ ! -d "/var/log/kolla/neutron" ]]; then
    mkdir -p /var/log/kolla/neutron
fi
if [[ $(stat -c %a /var/log/kolla/neutron) != "755" ]]; then
    chmod 755 /var/log/kolla/neutron
fi
if [[ ${KOLLA_BASE_DISTRO} == "centos" ]]; then
    export UPDATE_ALTERNATIVES="/usr/sbin/update-alternatives"
else
    export UPDATE_ALTERNATIVES="/usr/bin/update-alternatives"
fi

# set legacy iptables to allow kernels not supporting iptables-nft
# CentOS has update-alternatives 1.13, so use --display (not --query)
if $UPDATE_ALTERNATIVES --display iptables; then
    # NOTE(yoctozepto): Kolla-Ansible does not always set KOLLA_LEGACY_IPTABLES;
    # the workaround below ensures it gets set to `false` in such cases to fix
    # this code under `set -o nounset`.
    KOLLA_LEGACY_IPTABLES=${KOLLA_LEGACY_IPTABLES-false}

    if [[ $KOLLA_LEGACY_IPTABLES == "true" ]]; then
        sudo $UPDATE_ALTERNATIVES --set iptables /usr/sbin/iptables-legacy
        sudo $UPDATE_ALTERNATIVES --set ip6tables /usr/sbin/ip6tables-legacy
    else
        sudo $UPDATE_ALTERNATIVES --auto iptables
        sudo $UPDATE_ALTERNATIVES --auto ip6tables
    fi
fi

. /usr/local/bin/kolla_neutron_extend_start
