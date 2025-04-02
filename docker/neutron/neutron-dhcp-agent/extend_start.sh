if [[ ! -d "/var/log/kolla/neutron" ]]; then
    mkdir -p /var/log/kolla/neutron
fi
if [[ ! -f "/var/log/kolla/neutron/dnsmasq.log" ]]; then
    touch /var/log/kolla/neutron/dnsmasq.log
    chown neutron:kolla /var/log/kolla/neutron/dnsmasq.log
fi

if [[ "${KOLLA_NEUTRON_WRAPPERS:-false}" == "true" ]]; then
    echo "Copying neutron agent wrappers to /usr/local/bin"
    sudo -E /usr/local/lib/neutron-wrappers/copy-wrappers
else
    echo "Removing neutron agent wrappers from /usr/local/bin"
    sudo -E /usr/local/lib/neutron-wrappers/delete-wrappers
fi

. /usr/local/bin/kolla_neutron_extend_start
