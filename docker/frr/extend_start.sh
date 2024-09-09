#!/bin/bash

# Give processes executed with the "kolla" group the permission to create files
# and sub-directories in the /var/log/kolla directory.
#
# Also set the setgid permission on the /var/log/kolla directory so that new
# files and sub-directories in that directory inherit its group id ("kolla").

USERGROUP="frr:kolla"
FRR="frr"

if [ ! -d /var/log/kolla/frr ]; then
    mkdir -p /var/log/kolla/frr
fi
if [[ $(stat -c %U:%G /var/log/kolla/frr) != "${USERGROUP}" ]]; then
    sudo chown ${USERGROUP} /var/log/kolla/frr
fi
if [[ $(stat -c %a /var/log/kolla/frr) != "2775" ]]; then
    sudo chmod 2775 /var/log/kolla/frr
fi
if [[ (-d /var/lib/${FRR}) && ($(stat -c %U:%G /var/lib/${FRR}) != "${USERGROUP}") ]]; then
    sudo chown ${USERGROUP} /var/lib/${FRR}
fi
