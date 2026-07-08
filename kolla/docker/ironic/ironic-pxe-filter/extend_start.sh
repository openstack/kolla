#!/bin/bash
IRONIC_DHCP_HOSTS_DIR=${IRONIC_DHCP_HOSTS_DIR:-/etc/dnsmasq/dhcp-hostsdir}
DNSMASQ_PIDFILE=${DNSMASQ_PIDFILE:-/run/ironic/dnsmasq.pid}

# NOTE(wszumski): This container must be in same process namespace as dnsmasq
rm -f $IRONIC_DHCP_HOSTS_DIR/* && kill -HUP $(cat "$DNSMASQ_PIDFILE") || true
