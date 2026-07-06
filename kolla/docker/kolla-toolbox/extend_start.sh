#!/bin/bash

if [[ ! -f "/var/log/kolla/ansible.log" ]]; then
    touch /var/log/kolla/ansible.log
fi

if [[ $(stat -c %U:%G /var/log/kolla/ansible.log) != "ansible:kolla" ]]; then
    chown -R ansible:kolla /var/log/kolla/ansible.log
fi

if [[ $(stat -c %a /var/log/kolla/ansible.log) != "664" ]]; then
    chmod 664 /var/log/kolla/ansible.log
fi
