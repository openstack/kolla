if [[ "${KOLLA_NEUTRON_WRAPPERS:-false}" == "true" ]]; then
    echo "Copying neutron agent wrappers to /usr/local/bin"
    sudo -E /usr/local/lib/neutron-wrappers/copy-wrappers
else
    echo "Removing neutron agent wrappers from /usr/local/bin"
    sudo -E /usr/local/lib/neutron-wrappers/delete-wrappers
fi

. /usr/local/bin/kolla_neutron_extend_start
