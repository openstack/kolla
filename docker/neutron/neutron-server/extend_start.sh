#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/bash -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
    exit 0
fi

# Neutron uses rootwrap which requires a tty for sudo.
# Since the container is running in daemon mode, a tty
# is not present and requiretty must be commented out.
if [ ! -f /sudo-modified ]; then
    chmod 0640 /etc/sudoers
    sed -i '/Defaults    requiretty/s/^/#/' /etc/sudoers
    chmod 0440 /etc/sudoers
    touch /sudo-modified
fi
