#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

# Processing /var/lib/kolla/config_files/config.json as root.  This is necessary
# to permit certain files to be controlled by the root user which should
# not be writable by the dropped-privileged user, especially /run_command
sudo -E kolla_set_configs
CMD=$(cat /run_command)
ARGS=""

# Install/remove custom CA certificates
sudo kolla_copy_cacerts

# Install projects that are in /dev-mode
sudo kolla_install_projects

if [[ ! "${!KOLLA_SKIP_EXTEND_START[@]}" ]]; then
    # Run additional commands if present
    . kolla_extend_start
fi

echo "Running command: '${CMD}${ARGS:+ $ARGS}'"
exec ${CMD} ${ARGS}
