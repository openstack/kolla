#!/bin/bash
set -o errexit

# Wait for the log socket
if [[ ! "${!SKIP_LOG_SETUP[@]}" && -e /var/lib/kolla/heka ]]; then
    while [[ ! -S /var/lib/kolla/heka/log ]]; do
        sleep 1
    done
fi

# Processing /var/lib/kolla/config_files/config.json as root.  This is necessary
# to permit certain files to be controlled by the root user which should
# not be writable by the dropped-privileged user, especially /run_command
sudo -E kolla_set_configs
CMD=$(cat /run_command)
ARGS=""

if [[ ! "${!KOLLA_SKIP_EXTEND_START[@]}" ]]; then
    # Run additional commands if present
    source kolla_extend_start
fi

echo "Running command: '${CMD}${ARGS:+ $ARGS}'"
exec ${CMD} ${ARGS}
