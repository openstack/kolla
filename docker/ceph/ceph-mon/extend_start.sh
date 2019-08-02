#!/bin/bash

# Setup common paths
KEYRING_ADMIN="/etc/ceph/ceph.client.admin.keyring"
KEYRING_MON="/etc/ceph/ceph.client.mon.keyring"
KEYRING_RGW="/etc/ceph/ceph.client.radosgw.keyring"
MONMAP="/etc/ceph/ceph.monmap"
MON_DIR="/var/lib/ceph/mon/ceph-${HOSTNAME}"

if [[ ! -d "/var/log/kolla/ceph" ]]; then
    mkdir -p /var/log/kolla/ceph
fi
if [[ $(stat -c %a /var/log/kolla/ceph) != "755" ]]; then
    chmod 755 /var/log/kolla/ceph
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    # Lookup our fsid from the ceph.conf
    FSID=$(awk '/^fsid/ {print $3; exit}' /etc/ceph/ceph.conf)

    # Generating initial keyrings and monmap
    ceph-authtool --create-keyring "${KEYRING_MON}" --gen-key -n mon. --cap mon 'allow *'
    ceph-authtool --create-keyring "${KEYRING_ADMIN}" --gen-key -n client.admin --cap mon 'allow *' --cap osd 'allow *' --cap mds 'allow *' --cap mgr 'allow *'
    ceph-authtool --create-keyring "${KEYRING_RGW}" --gen-key -n client.radosgw.gateway --cap osd 'allow rwx' --cap mon 'allow rwx'
    ceph-authtool "${KEYRING_MON}" --import-keyring "${KEYRING_ADMIN}"
    ceph-authtool "${KEYRING_MON}" --import-keyring "${KEYRING_RGW}"
    monmaptool --create --add "${HOSTNAME}" "${MON_IP}" --fsid "${FSID}" "${MONMAP}"

    exit 0
fi

# This section runs on every mon that does not have a keyring already.
if [[ ! -e "${MON_DIR}/keyring" ]]; then
    KEYRING_TMP="/tmp/ceph.mon.keyring"

    # Generate keyring for current monitor
    ceph-authtool --create-keyring "${KEYRING_TMP}" --import-keyring "${KEYRING_ADMIN}"
    ceph-authtool "${KEYRING_TMP}" --import-keyring "${KEYRING_MON}"
    mkdir -p "${MON_DIR}"

    mon_stat=$(ceph mon stat --connect-timeout 1 || true)
    mon_check=$(echo $mon_stat | awk '/mons/{print $0}' | wc -l)
    if [[ ${mon_check} -eq 0 ]]; then
        ceph-mon --mkfs -i "${HOSTNAME}" --keyring "${KEYRING_TMP}"
    else
        MONMAP_TMP="/tmp/ceph.${HOSTNAME}.monmap"
        ceph mon getmap -o "${MONMAP_TMP}"
        ceph-mon --mkfs -i "${HOSTNAME}" --monmap "${MONMAP_TMP}" --keyring "${KEYRING_TMP}"
        rm "${MONMAP_TMP}"
    fi
    rm "${KEYRING_TMP}"
fi
