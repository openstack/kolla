#!/bin/bash

# Neutron uses rootwrap which requires a tty for sudo.
# Since the container is running in daemon mode, a tty
# is not present and requiretty must be commented out.
if [ ! -f /sudo-modified ]; then
    chmod 0640 /etc/sudoers
    sed -i '/Defaults    requiretty/s/^/#/' /etc/sudoers
    chmod 0440 /etc/sudoers
    touch /sudo-modified
fi
