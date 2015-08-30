#!/bin/bash
set -o errexit

CMD="/usr/bin/ceph-osd"
ARGS="-f -d -i ${OSD_ID} --osd-journal ${OSD_DIR}/journal -k ${OSD_DIR}/keyring"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    # Creating a new label for the disk
    parted "${OSD_DEV}" -s -- mklabel gpt

    # Preparing the OSD for use with Ceph
    ceph-disk prepare "${OSD_DEV}"
    OSD_ID="$(ceph osd create)"
    OSD_DIR="/var/lib/ceph/osd/ceph-${OSD_ID}"
    mkdir -p "${OSD_DIR}"
    mount "${OSD_DEV}1" "${OSD_DIR}"
    ceph-osd -i "${OSD_ID}" --mkfs --mkkey
    ceph auth add "osd.${OSD_ID}" osd 'allow *' mon 'allow proflie osd' -i "${OSD_DIR}/keyring"

    # Adding osd to crush map
    ceph osd crush add-bucket "$(hostname)" host
    ceph osd crush move "$(hostname)" root=default
    ceph osd crush add "${OSD_ID}" "${OSD_INITIAL_WEIGHT}" host="$(hostname)"
    exit 0
fi

exec $CMD $ARGS
