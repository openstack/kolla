#!/bin/bash
set -o errexit

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
