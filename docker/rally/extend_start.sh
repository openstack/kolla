#!/bin/bash

if [[ ! -d "/var/log/kolla/rally" ]]; then
    mkdir -p /var/log/kolla/rally
fi
if [[ $(stat -c %a /var/log/kolla/rally) != "755" ]]; then
    chmod 755 /var/log/kolla/rally
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    # NOTE(osmanlicilegi): "rally-manage db" command was deprecated since 0.10.0 but
    # Ubuntu ships 0.9.1 for Bionic.
    if [[ ${KOLLA_BASE_DISTRO} == "ubuntu" && ${KOLLA_INSTALL_TYPE} == "binary" ]]; then
        rally-manage db create || rally-manage db upgrade
    else
        rally db create || rally db upgrade
    fi
    exit 0
fi
