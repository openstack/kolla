#!/bin/bash
set -o errexit

# Loading common functions.
source /opt/kolla/kolla-common.sh

# Generate run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    su -s /bin/bash -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
    exit 0
fi

exec $CMD
