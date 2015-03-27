#!/bin/sh

# If libvirt is not installed on the host permissions need to be set
# If running in qemu, we don't need to set anything as /dev/kvm won't exist
if [[ -c /dev/kvm ]]; then
    chmod 660 /dev/kvm
    chown root:kvm /dev/kvm
fi

echo "Starting libvirtd."
exec /usr/sbin/libvirtd
