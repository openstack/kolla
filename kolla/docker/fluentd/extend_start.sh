#!/bin/bash

if [[ (-d /var/lib/fluentd) && ($(stat -c %U:%G /var/lib/fluentd) != "fluentd:kolla") ]]; then
    sudo chown fluentd:kolla /var/lib/fluentd
fi
