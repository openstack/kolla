#!/bin/bash

if [[ ! -d "/var/log/kolla/logstash" ]]; then
    mkdir -p /var/log/kolla/logstash
fi
if [[ $(stat -c %a /var/log/kolla/logstash) != "755" ]]; then
    chmod 755 /var/log/kolla/logstash
fi
