#!/bin/bash

DNSMASQ_PIDFILE=${DNSMASQ_PIDFILE:-/run/ironic/dnsmasq.pid}
DNSMASQ_PIDFILE_DIR="$(dirname $DNSMASQ_PIDFILE)"

if [[ ! -d "/var/log/kolla/ironic" ]]; then
    mkdir -p /var/log/kolla/ironic
fi
if [[ $(stat -c %a /var/log/kolla/ironic) != "755" ]]; then
    chmod 755 /var/log/kolla/ironic
fi
if [[ ! -r "/var/log/kolla/ironic/dnsmasq.log" ]]; then
    touch /var/log/kolla/ironic/dnsmasq.log
    chown ironic:ironic /var/log/kolla/ironic/dnsmasq.log
fi

if [[ ! -d "$DNSMASQ_PIDFILE_DIR" ]]; then
    mkdir -p "$DNSMASQ_PIDFILE_DIR"
fi

# NOTE(wszumski): This writes the PID of dnsmasq out to a file. The PIDFILE can be used in
# another container to send a signal to dnsmasq to reload its config (providing that the two
# containers share a PID namespace). The concrete use case is for the Ironic PXE filter to
# clean up stale host entries on startup as documented in:
#
# https://docs.openstack.org/ironic/latest/admin/inspection/pxe_filter.html
#
# We cannot use the pid-file option in dnsmasq, since it will only write the PIDFILE if you
# run dnsmasq in its non-forking mode i.e you do use the --no-daemon or --keep-in-foreground
# options.
echo $$ > "$DNSMASQ_PIDFILE"
