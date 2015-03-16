#!/bin/sh

# If libvirt is not installed on the host permissions need to be set
chmod 660 /dev/kvm
chown root:kvm /dev/kvm

echo "Starting libvirtd."
exec /usr/sbin/libvirtd
