#!/bin/bash

# TODO(SamYaple): Tweak libvirt.conf rather than change permissions.
# Fix permissions for libvirt
# Do not remove unless CentOS has been validated
if [[ -c /dev/kvm ]]; then
    chmod 660 /dev/kvm
    chown root:kvm /dev/kvm
fi

# Mount xenfs for libxl to work
if [[ $(lsmod | grep xenfs) ]]; then
    mount -t xenfs xenfs /proc/xen
fi

if [[ ! -d "/var/log/kolla/libvirt" ]]; then
    mkdir -p /var/log/kolla/libvirt
    touch /var/log/kolla/libvirt/libvirtd.log
    chmod 644 /var/log/kolla/libvirt/libvirtd.log
fi
if [[ $(stat -c %a /var/log/kolla/libvirt) != "755" ]]; then
    chmod 755 /var/log/kolla/libvirt
    chmod 644 /var/log/kolla/libvirt/libvirtd.log
fi
