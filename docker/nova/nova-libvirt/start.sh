#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

# TODO(SamYaple): Tweak libvirt.conf rather than change permissions.
# Fix permissions for libvirt
# Do not remove unless CentOS has been validated
if [[ -c /dev/kvm ]]; then
    chmod 660 /dev/kvm
    chown root:kvm /dev/kvm
fi

exec $CMD
