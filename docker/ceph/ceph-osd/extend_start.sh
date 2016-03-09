#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    # Wait for ceph quorum before proceeding
    ceph quorum_status

    # Formatting disk for ceph
    sgdisk --zap-all -- "${OSD_DEV}"
    sgdisk --new=2:1M:5G --change-name=2:KOLLA_CEPH_JOURNAL --typecode=2:45B0969E-9B03-4F30-B4C6-B4B80CEFF106 --mbrtogpt -- "${OSD_DEV}"
    sgdisk --largest-new=1 --change-name=1:KOLLA_CEPH_DATA --typecode=1:4FBD7E29-9D25-41B8-AFD0-062C0CEFF05D -- "${OSD_DEV}"
    # This command may throw errors that we can safely ignore
    partprobe || true

    count=0
    while [[ "${OSD_PARTITION}x" == "x" ]]; do
        if [[ "${count}" -gt 5 ]]; then
            echo "Could not find OSD Partition"
            exit 1
        fi
        sleep 1
        # We look up the appropriate device path with partition.
        OSD_PARTITION=$(ls "${OSD_DEV}"* | egrep "${OSD_DEV}p?1")
        count=$(( count + 1 ))
    done
    JOURNAL_PARTITION="${OSD_PARTITION%?}2"

    OSD_ID=$(ceph osd create)
    OSD_DIR="/var/lib/ceph/osd/ceph-${OSD_ID}"
    mkdir -p "${OSD_DIR}"
    mkfs.xfs -f "${OSD_PARTITION}"
    mount "${OSD_PARTITION}" "${OSD_DIR}"

    # This will through an error about no key existing. That is normal. It then
    # creates the key in the next step.
    ceph-osd -i "${OSD_ID}" --mkfs --osd-journal="${JOURNAL_PARTITION}" --mkkey
    ceph auth add "osd.${OSD_ID}" osd 'allow *' mon 'allow profile osd' -i "${OSD_DIR}/keyring"
    umount "${OSD_PARTITION}"

    if [[ "${!CEPH_CACHE[@]}" ]]; then
        CEPH_ROOT_NAME=cache
    fi

    # These commands only need to be run once per host but are safe to run
    # repeatedly. This can be improved later or if any problems arise.
    ceph osd crush add-bucket "$(hostname)${CEPH_ROOT_NAME:+-${CEPH_ROOT_NAME}}" host
    ceph osd crush move "$(hostname)${CEPH_ROOT_NAME:+-${CEPH_ROOT_NAME}}" root=${CEPH_ROOT_NAME:-default}

    # Adding osd to crush map
    ceph osd crush add "${OSD_ID}" "${OSD_INITIAL_WEIGHT}" host="$(hostname)${CEPH_ROOT_NAME:+-${CEPH_ROOT_NAME}}"
    exit 0
fi

# We look up the appropriate journal since we cannot rely on symlinks
JOURNAL_PARTITION=$(ls "${OSD_DEV}"* | egrep "${OSD_DEV}p?2")
OSD_DIR="/var/lib/ceph/osd/ceph-${OSD_ID}"
ARGS="-i ${OSD_ID} --osd-journal ${JOURNAL_PARTITION} -k ${OSD_DIR}/keyring"
