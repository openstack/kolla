#!/bin/bash

# Give processes executed with the "kolla" group the permission to create files
# and sub-directories in the /var/log/kolla directory.
#
# Also set the setgid permission on the /var/log/kolla directory so that new
# files and sub-directories in that directory inherit its group id ("kolla").

USERGROUP="ovn-bgp-agent:kolla"
OVNBGPAGENT="ovn-bgp-agent"

if [[ (-d /var/lib/${OVNBGPAGENT}) && ($(stat -c %U:%G /var/lib/${OVNBGPAGENT}) != "${USERGROUP}") ]]; then
    sudo chown ${USERGROUP} /var/lib/${OVNBGPAGENT}
fi
