#!/bin/bash
set -o errexit

CMD="/usr/bin/neutron-l3-agent"
ARGS="--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/l3_agent.ini --config-file /etc/neutron/fwaas_driver.ini --config-file /etc/neutron/plugins/ml2/ml2_conf.ini"

# Loading common functions.
source /opt/kolla/kolla-common.sh
source /opt/kolla/config-sudoers.sh

# Override set_configs() here because it doesn't work for fat containers like
# this one.
set_configs() {
    case $KOLLA_CONFIG_STRATEGY in
        CONFIG_EXTERNAL_COPY_ALWAYS)
            source /opt/kolla/neutron-l3-agent/config-external.sh
            ;;
        CONFIG_EXTERNAL_COPY_ONCE)
            if [[ -f /configured-l3 ]]; then
                echo 'INFO - Neutron-l3 has already been configured; Refusing to copy new configs'
                return
            fi
            source /opt/kolla/neutron-l3-agent/config-external.sh
            touch /configured-l3
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
