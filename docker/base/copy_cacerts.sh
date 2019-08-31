#!/bin/bash

# Copy custom CA certificates to system trusted CA certificates folder
# and run CA update utility

# Remove old certificates
rm -f /usr/local/share/ca-certificates/kolla-customca-* \
        /etc/pki/ca-trust/source/anchors/kolla-customca-*

if [[ -d /var/lib/kolla/config_files/ca-certificates ]] && \
        [[ ! -z "$(ls -A /var/lib/kolla/config_files/ca-certificates/)" ]]; then
    if [[ -e /etc/debian_version ]]; then
        # Debian, Ubuntu
        for cert in /var/lib/kolla/config_files/ca-certificates/*; do
            file=$(basename "$cert")
            cp $cert "/usr/local/share/ca-certificates/kolla-customca-$file"
        done
        update-ca-certificates
    elif [[ -e /etc/redhat-release ]]; then
        # CentOS, RHEL
        for cert in /var/lib/kolla/config_files/ca-certificates/*; do
            file=$(basename "$cert")
            cp $cert "/etc/pki/ca-trust/source/anchors/kolla-customca-$file"
        done
        update-ca-trust
    fi
fi
