#!/bin/bash

sudo find /srv/node/ -maxdepth 1 -type d -execdir chown swift:swift {} \+
mkdir -p /var/lib/swift/lock
