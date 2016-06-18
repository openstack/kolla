#!/bin/bash

if [[ ! -d "/var/log/kolla/ceph" ]]; then
    mkdir -p /var/log/kolla/ceph
fi
if [[ $(stat -c %a /var/log/kolla/ceph) != "755" ]]; then
    chmod 755 /var/log/kolla/ceph
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    # NOTE(SamYaple): Static gpt partcodes
    CEPH_JOURNAL_TYPE_CODE="45B0969E-9B03-4F30-B4C6-B4B80CEFF106"
    CEPH_OSD_TYPE_CODE="4FBD7E29-9D25-41B8-AFD0-062C0CEFF05D"

    # Wait for ceph quorum before proceeding
    ceph quorum_status

    if [[ "${USE_EXTERNAL_JOURNAL}" == "False" ]]; then
        # Formatting disk for ceph
        sgdisk --zap-all -- "${OSD_DEV}"
        sgdisk --new=2:1M:5G -- "${JOURNAL_DEV}"
        sgdisk --largest-new=1 -- "${OSD_DEV}"
        # NOTE(SamYaple): This command may throw errors that we can safely ignore
        partprobe || true

    fi

    OSD_ID=$(ceph osd create)
    OSD_DIR="/var/lib/ceph/osd/ceph-${OSD_ID}"
    mkdir -p "${OSD_DIR}"

    if [[ "${OSD_FILESYSTEM}" == "btrfs" ]]; then
        mkfs.btrfs -f "${OSD_PARTITION}"
    elif [[ "${OSD_FILESYSTEM}" == "ext4" ]]; then
        mkfs.ext4 "${OSD_PARTITION}"
    else
        mkfs.xfs -f "${OSD_PARTITION}"
    fi
    mount "${OSD_PARTITION}" "${OSD_DIR}"

    # This will through an error about no key existing. That is normal. It then
    # creates the key in the next step.
    ceph-osd -i "${OSD_ID}" --mkfs --osd-journal="${JOURNAL_PARTITION}" --mkkey
    ceph auth add "osd.${OSD_ID}" osd 'allow *' mon 'allow profile osd' -i "${OSD_DIR}/keyring"
    umount "${OSD_PARTITION}"

    if [[ "${!CEPH_CACHE[@]}" ]]; then
        CEPH_ROOT_NAME=cache
    fi

    if [[ "${OSD_INITIAL_WEIGHT}" == "auto" ]]; then
        OSD_INITIAL_WEIGHT=$(parted --script ${OSD_PARTITION} unit TB print | awk 'match($0, /^Disk.* (.*)TB/, a){printf("%.2f", a[1])}')
    fi

    # These commands only need to be run once per host but are safe to run
    # repeatedly. This can be improved later or if any problems arise.
    ceph osd crush add-bucket "${HOSTNAME}${CEPH_ROOT_NAME:+-${CEPH_ROOT_NAME}}" host
    ceph osd crush move "${HOSTNAME}${CEPH_ROOT_NAME:+-${CEPH_ROOT_NAME}}" root=${CEPH_ROOT_NAME:-default}

    # Adding osd to crush map
    ceph osd crush add "${OSD_ID}" "${OSD_INITIAL_WEIGHT}" host="${HOSTNAME}${CEPH_ROOT_NAME:+-${CEPH_ROOT_NAME}}"

    # Setting partition name based on ${OSD_ID}
    sgdisk "--change-name=${OSD_PARTITION_NUM}:KOLLA_CEPH_DATA_${OSD_ID}" "--typecode=${OSD_PARTITION_NUM}:${CEPH_OSD_TYPE_CODE}" -- "${OSD_DEV}"
    sgdisk "--change-name=${JOURNAL_PARTITION_NUM}:KOLLA_CEPH_DATA_${OSD_ID}_J" "--typecode=${JOURNAL_PARTITION_NUM}:${CEPH_JOURNAL_TYPE_CODE}" -- "${JOURNAL_DEV}"

    exit 0
fi

OSD_DIR="/var/lib/ceph/osd/ceph-${OSD_ID}"
ARGS="-i ${OSD_ID} --osd-journal ${JOURNAL_PARTITION} -k ${OSD_DIR}/keyring"
