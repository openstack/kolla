#!/bin/bash

set -o errexit

CMD="/usr/bin/ceph-mon"
ARGS="-d -i $(hostname) --public-addr ${MON_IP}:6789"

# Setup common paths
KEYRING_ADMIN="/etc/ceph/ceph.client.admin.keyring"
KEYRING_MON="/etc/ceph/ceph.client.mon.keyring"
MONMAP="/etc/ceph/ceph.monmap"
MON_DIR="/var/lib/ceph/mon/ceph-$(hostname)"

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Execute config strategy
set_configs

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    # Lookup our fsid from the ceph.conf
    FSID=$(awk '/^fsid/ {print $3; exit}' /etc/ceph/ceph.conf)

    # Generating initial keyrings and monmap
    ceph-authtool --create-keyring "${KEYRING_MON}" --gen-key -n mon. --cap mon 'allow *'
    ceph-authtool --create-keyring "${KEYRING_ADMIN}" --gen-key -n client.admin --set-uid=0 --cap mon 'allow *' --cap osd 'allow *' --cap mds 'allow'
    ceph-authtool "${KEYRING_MON}" --import-keyring "${KEYRING_ADMIN}"
    monmaptool --create --add "$(hostname)" "${MON_IP}" --fsid "${FSID}" "${MONMAP}"

    echo "Sleeping until keys are fetched"
    /bin/sleep infinity
fi

# This section runs on every mon that does not have a keyring already.
if [[ ! -e "${MON_DIR}/keyring" ]]; then
    KEYRING_TMP="/tmp/ceph.mon.keyring"

    # Generate keyring for current monitor
    ceph-authtool --create-keyring "${KEYRING_TMP}" --import-keyring "${KEYRING_ADMIN}"
    ceph-authtool "${KEYRING_TMP}" --import-keyring "${KEYRING_MON}"
    mkdir -p "${MON_DIR}"
    ceph-mon --mkfs -i "$(hostname)" --monmap "${MONMAP}" --keyring "${KEYRING_TMP}"
    rm "${KEYRING_TMP}"
fi

exec $CMD $ARGS
