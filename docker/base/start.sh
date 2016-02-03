#!/bin/bash
set -o errexit

# TODO(SamYaple): After we merge Heka it should be possible to remove
# this symlink, investigate that after Heka is finalized
# NOTE(SamYaple): Setting up logging socket to /dev/log
if [[ ! "${!SKIP_LOG_SETUP[@]}" && -e /var/lib/kolla/rsyslog ]]; then
    while [[ ! -S /var/lib/kolla/rsyslog/log ]]; do
        sleep 1
    done
    sudo ln -sf /var/lib/kolla/rsyslog/log /dev/log
fi

# Wait for the log socket
if [[ ! "${!SKIP_LOG_SETUP[@]}" && -e /var/lib/kolla/heka ]]; then
    while [[ ! -S /var/lib/kolla/heka/log ]]; do
        sleep 1
    done
fi

# Processing /var/lib/kolla/config_files/config.json as root.  This is necessary
# to permit certain files to be controlled by the root user which should
# not be writable by the dropped-privileged user, especially /run_command
sudo -E kolla_set_configs
CMD=$(cat /run_command)
ARGS=""

# Run additional commands if present
source kolla_extend_start

echo "Running command: '${CMD}${ARGS:+ $ARGS}'"
exec ${CMD} ${ARGS}
