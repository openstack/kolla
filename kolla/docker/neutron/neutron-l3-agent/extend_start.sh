#!/bin/bash
if [[ ! -d "/var/log/kolla/neutron" ]]; then
    mkdir -p /var/log/kolla/neutron
fi
if [[ $(stat -c %a /var/log/kolla/neutron) != "755" ]]; then
    chmod 755 /var/log/kolla/neutron
fi

# NOTE(hrw): from RHEL 9 release notes:
# "Iptables-nft and ipset are now deprecated, which included the utilities,
#  iptables, ip6tables, ebtables, and arptables. These are all replaced by the
#  nftables framework."
# so no need to even use u-a on RHEL 9 family as there is one provider
# (and there is no u-a for ip6tables so script fails)
if [[ ! ${KOLLA_BASE_DISTRO} =~ centos|rocky ]]; then
    if /usr/bin/update-alternatives --display iptables; then
        # NOTE(yoctozepto): Kolla-Ansible does not always set KOLLA_LEGACY_IPTABLES;
        # the workaround below ensures it gets set to `false` in such cases to fix
        # this code under `set -o nounset`.
        KOLLA_LEGACY_IPTABLES=${KOLLA_LEGACY_IPTABLES-false}
        if [[ $KOLLA_LEGACY_IPTABLES == "true" ]]; then
            sudo /usr/bin/update-alternatives --set iptables /usr/sbin/iptables-legacy
            sudo /usr/bin/update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
        else
            sudo /usr/bin/update-alternatives --auto iptables
            sudo /usr/bin/update-alternatives --auto ip6tables
        fi
    fi
fi

if [[ "${KOLLA_NEUTRON_WRAPPERS:-false}" == "true" ]]; then
    echo "Copying neutron agent wrappers to /usr/local/bin"
    sudo -E /usr/local/lib/neutron-wrappers/copy-wrappers
else
    echo "Removing neutron agent wrappers from /usr/local/bin"
    sudo -E /usr/local/lib/neutron-wrappers/delete-wrappers
fi

. /usr/local/bin/kolla_neutron_extend_start
