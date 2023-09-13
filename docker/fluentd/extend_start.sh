#!/bin/bash

# Give processes executed with the "kolla" group the permission to create files
# and sub-directories in the /var/log/kolla directory.
#
# Also set the setgid permission on the /var/log/kolla directory so that new
# files and sub-directories in that directory inherit its group id ("kolla").

if [ ! -d /var/log/kolla ]; then
    mkdir -p /var/log/kolla
fi
if [[ $(stat -c %U:%G /var/log/kolla) != "fluentd:kolla" ]]; then
    sudo chown fluentd:kolla /var/log/kolla
fi
if [[ $(stat -c %a /var/log/kolla) != "2775" ]]; then
    sudo chmod 2775 /var/log/kolla
fi
if [[ (-d /var/lib/fluentd) && ($(stat -c %U:%G /var/lib/fluentd) != "fluentd:kolla") ]]; then
    sudo chown fluentd:kolla /var/lib/fluentd
fi
