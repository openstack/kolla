#!/bin/bash

EXTRA_KEYSTONE_MANAGE_ARGS=${EXTRA_KEYSTONE_MANAGE_ARGS-}
# Upgrade and exit if KOLLA_UPGRADE variable is set. This catches all cases
# of the KOLLA_UPGRADE variable being set, including empty.
if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    # TODO(duonghq): check doctor result here
    # TODO: find reason why doctor failed in gate
    # sudo -H -u keystone keystone-manage doctor
    sudo -H -u keystone keystone-manage ${EXTRA_KEYSTONE_MANAGE_ARGS} db_sync --expand
    sudo -H -u keystone keystone-manage ${EXTRA_KEYSTONE_MANAGE_ARGS} db_sync --migrate
    exit 0
fi

# Contract database and exit if KOLLA_FINISH_UPGRADE variable is set.
# This catches all cases of the KOLLA_FINISH_UPGRADE variable being set,
# including empty.
if [[ "${!KOLLA_FINISH_UPGRADE[@]}" ]]; then
    sudo -H -u keystone keystone-manage ${EXTRA_KEYSTONE_MANAGE_ARGS} db_sync --contract
    exit 0
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    sudo -H -u keystone keystone-manage ${EXTRA_KEYSTONE_MANAGE_ARGS} db_sync
    exit 0
fi
