#!/bin/bash

# The script will create the cinder-volume volume group that will
# allow cinder to create volumes from a backing file.
# This is based off devstack.
set -e

backing_file=/opt/data/cinder_volume

check_required_vars CINDER_LVM_LO_VOLUME_SIZE CINDER_VOLUME_GROUP

if ! vgs ${CINDER_VOLUME_GROUP}; then
    [[ ! -f $backing_file ]] && truncate -s ${CINDER_LVM_LO_VOLUMES_SIZE} $backing_file
    vg_dev=`losetup -f --show $backing_file`
    if ! vgs ${CINDER_VOLUME_GROUP}; then
        vgcreate ${CINDER_VOLUME_GROUP} $vg_dev
    fi
fi

# Remove iscsi targets
cinder-rtstool get-targets | xargs -rn 1 cinder-rtstool delete

