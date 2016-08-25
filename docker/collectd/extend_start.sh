#!/bin/bash

# Only update permissions if permissions need to be updated
if [[ $(stat -c %U:%G /var/lib/collectd) != "collectd:collectd" ]]; then
    sudo chown collectd: /var/lib/collectd
fi