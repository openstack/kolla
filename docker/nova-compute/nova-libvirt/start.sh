#!/bin/sh
/bin/chmod 666 /dev/kvm

echo "Starting guests."
/usr/libexec/libvirt-guests.sh start

echo "Starting virtlockd."
/usr/sbin/virtlockd &

sleep 3

echo "Starting libvirtd."
exec /usr/sbin/libvirtd --listen
