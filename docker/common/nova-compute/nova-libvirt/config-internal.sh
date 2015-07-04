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

# https://bugs.launchpad.net/kolla/+bug/1461635
# Cinder requires mounting /dev in the cinder-volume, nova-compute,
# and libvirt containers.  If /dev/pts/ptmx does not have proper permissions
# on the host, then libvirt will fail to boot an instance.
# This is a bug in Docker where it is not correctly mounting /dev/pts
# Tech Debt tracker: https://bugs.launchpad.net/kolla/+bug/1468962
# **Temporary fix**
chmod 666 /dev/pts/ptmx

echo "Starting libvirtd."
exec /usr/sbin/libvirtd
