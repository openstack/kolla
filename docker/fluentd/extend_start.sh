#!/bin/bash

# Give processes executed with the "kolla" group the permission to create files
# and sub-directories in the /var/log/kolla directory.
#
# Also set the setgid permission on the /var/log/kolla directory so that new
# files and sub-directories in that directory inherit its group id ("kolla").
if [[ $(stat -c %U:%G /var/log/kolla) != "td-agent:kolla" ]]; then
    sudo chown td-agent:kolla /var/log/kolla
fi
if [[ $(stat -c %a /var/log/kolla) != "2775" ]]; then
    sudo chmod 2775 /var/log/kolla
fi
if [[ $(stat -c %U:%G /var/lib/td-agent) != "td-agent:kolla" ]]; then
    sudo chown td-agent:kolla /var/lib/td-agent
fi
