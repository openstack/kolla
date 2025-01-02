if [[ ! -d "/var/log/kolla/neutron" ]]; then
    mkdir -p /var/log/kolla/neutron
fi
if [[ ! -f "/var/log/kolla/neutron/dnsmasq.log" ]]; then
    touch /var/log/kolla/neutron/dnsmasq.log
    chown neutron:kolla /var/log/kolla/neutron/dnsmasq.log
fi

. /usr/local/bin/kolla_neutron_extend_start
