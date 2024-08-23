#!/bin/bash

if [[ ! -e "/var/log/kolla/libvirt/libvirtd.log" ]]; then
    mkdir -p /var/log/kolla/libvirt
    touch /var/log/kolla/libvirt/libvirtd.log
    chmod 644 /var/log/kolla/libvirt/libvirtd.log
fi
if [[ $(stat -c %a /var/log/kolla/libvirt) != "755" ]]; then
    chmod 755 /var/log/kolla/libvirt
    chmod 644 /var/log/kolla/libvirt/libvirtd.log
fi
