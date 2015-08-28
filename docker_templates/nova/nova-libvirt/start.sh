#!/bin/bash
set -o errexit

CMD="/usr/sbin/libvirtd"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

# TODO(SamYaple): Tweak libvirt.conf rather than change permissions.
# Fix permissions for libvirt
if [[ -c /dev/kvm ]]; then
    chmod 660 /dev/kvm
    chown root:kvm /dev/kvm
fi

exec $CMD $ARGS
