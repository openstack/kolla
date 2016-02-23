#!/bin/bash

if [[ ! -d "/var/log/kolla/mistral" ]]; then
    mkdir -p /var/log/kolla/mistral
fi
if [[ $(stat -c %a /var/log/kolla/mistral) != "755" ]]; then
    chmod 755 /var/log/kolla/mistral
fi

source /usr/local/bin/kolla_mistral_extend_start
