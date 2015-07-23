#!/bin/bash
set -o errexit

CMD="/usr/sbin/libvirtd"
ARGS=""

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Config-internal script exec out of this function, it does not return here.
set_configs

# TODO(SamYaple): Unify this with config-internal. Tweak libvirt.conf rather
#                 than change permissions.
# Fix permissions for libvirt
if [[ -c /dev/kvm ]]; then
    chmod 660 /dev/kvm
    chown root:kvm /dev/kvm
fi

exec $CMD $ARGS
