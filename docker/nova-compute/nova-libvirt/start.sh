#!/bin/bash

if [[ $(cat /proc/cpuinfo | grep vmx) ]]; then
    modprobe kvm_intel
elif [[ $(cat /proc/cpuinfo | grep svm) ]]; then
    modprobe kvm_amd
else
    echo "WARNING: Your hardware does not support hardware virtualization -" \
         "using qemu software virtualization instead"
fi

modprobe ip6_tables ip_tables ebtable_nat

# If libvirt is not installed on the host permissions need to be set
# If running in qemu, we don't need to set anything as /dev/kvm won't exist
if [[ -c /dev/kvm ]]; then
    chmod 660 /dev/kvm
    chown root:kvm /dev/kvm
fi

echo "Starting libvirtd."
exec /usr/sbin/libvirtd
