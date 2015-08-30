#!/bin/bash
set -o errexit

CMD="/usr/bin/neutron-dhcp-agent"
ARGS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/dhcp_agent.ini"

# Loading common functions.
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-sudoers.sh

# Override set_configs() here because it doesn't work for fat containers like
# this one.
set_configs() {
    case $KOLLA_CONFIG_STRATEGY in
        COPY_ALWAYS)
            source /opt/kolla/neutron-dhcp-agent/config-external.sh
            ;;
        COPY_ONCE)
            if [[ -f /configured-dhcp ]]; then
                echo 'INFO - Neutron-dhcp has already been configured; Refusing to copy new configs'
                return
            fi
            source /opt/kolla/neutron-dhcp-agent/config-external.sh
            touch /configured-dhcp
            ;;

        *)
            echo '$KOLLA_CONFIG_STRATEGY is not set properly'
            exit 1
            ;;
    esac
}

# Execute config strategy
set_configs

exec $CMD $ARGS
