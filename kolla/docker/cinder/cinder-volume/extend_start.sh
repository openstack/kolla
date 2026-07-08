#!/bin/bash

if [[ $(stat -c %U:%G /var/lib/cinder) != "cinder:kolla" ]]; then
    sudo chown -R cinder:kolla /var/lib/cinder
fi
if [[ $(stat -c %a /var/lib/cinder) != "2775" ]]; then
    sudo chmod 2775 /var/lib/cinder
fi
if [[ $(stat -c %U:%G /etc/iscsi) != "cinder:kolla" ]]; then
    sudo chown -R cinder:kolla /etc/iscsi
fi
if [[ $(stat -c %a /etc/iscsi) != "2775" ]]; then
    sudo chmod 2775 /etc/iscsi
fi
