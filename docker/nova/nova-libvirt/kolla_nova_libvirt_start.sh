#!/bin/bash
set -euo pipefail

# NOTE(mikal): Start virtlogd as a sidecar. We need this for
# nova instance console logs to rotate. Otherwise they will
# consume unbounded amounts of disk.
#
# No exec here: libvirtd will be the "main" process.
/usr/sbin/virtlogd &

# Now hand over PID 1's direct child role to libvirtd.
exec /usr/sbin/libvirtd --listen
