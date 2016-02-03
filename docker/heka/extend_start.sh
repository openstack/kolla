#!/bin/bash

# Give processes executed with the "kolla" group the permission to create files
# and sub-directories in the /var/log/kolla directory.
#
# Also set the setgid permission on the /var/log/kolla directory so that new
# files and sub-directories in that directory inherit its group id ("kolla").
if [[ $(stat -c %U:%G /var/log/kolla) != "heka:kolla" ]]; then
    sudo chown heka:kolla /var/log/kolla
fi
if [[ $(stat -c %a /var/log/kolla) != "2775" ]]; then
    sudo chmod 2775 /var/log/kolla
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    exit 0
fi

# /var/cache/hekad is what the Heka daemon will use for persistent storage
# through process restarts, so make "heka" the user of that directory.
if [[ $(stat -c %U:%G /var/cache/hekad) != "heka:heka" ]]; then
    sudo chown heka: /var/cache/hekad
fi

# Give hekad the permission to create the "log" Unix socket file in the
# /var/lib/kolla/heka directory.
if [[ $(stat -c %U:%G /var/lib/kolla/heka) != "heka:kolla" ]]; then
    sudo chown heka:kolla /var/lib/kolla/heka
fi

# The Heka daemon will create the /var/lib/kolla/heka/log Unix socket file, so
# make sure it's not present or the Heka daemon will fail when starting.
if [[ -e "/var/lib/kolla/heka/log" ]]; then
    rm -rf /var/lib/kolla/heka/log
fi
