#!/bin/bash

# Copy custom CA certificates to system trusted CA certificates folder
# and run CA update utility

if [[ -e "/etc/debian_version" ]]; then
    ca_dst_path="/usr/local/share/ca-certificates"
    update_command="update-ca-certificates"
elif [[ -e "/etc/redhat-release" ]]; then
    ca_dst_path="/etc/pki/ca-trust/source/anchors"
    update_command="update-ca-trust"
else
    echo "Unsupported OS"
    exit 1
fi

# Initialize update_needed variable
update_needed="false"

# Remove old certificates
if find /etc/ssl/certs/ \
        /usr/local/share/ca-certificates/ \
        /etc/pki/ca-trust/source/anchors/ \
        -name 'kolla*' -exec rm -f {} + 2>/dev/null; then
    update_needed="true"
fi

# Determine source path for CA certificates
if grep -q '"source": "/var/lib/kolla/share/ca-certificates"' /etc/kolla/defaults/state; then
    ca_src_path="/var/lib/kolla/share/ca-certificates"
else
    ca_src_path="/var/lib/kolla/config_files/ca-certificates"
fi

# Check if the source path exists and is not empty
if [[ -d ${ca_src_path} && $(ls -A "${ca_src_path}" 2>/dev/null) ]]; then
    # Copy certificates and update CA
    for cert in "${ca_src_path}"/*; do
        file=$(basename "${cert}")
        cp ${cert} ${ca_dst_path}/kolla-customca-${file}
        update_needed="true"
    done
fi

# Run the update command if needed
if [[ "${update_needed}" == "true" ]]; then
    ${update_command}
fi
