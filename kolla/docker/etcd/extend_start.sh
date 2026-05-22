#!/bin/bash

if [[ $(stat -c %U /var/lib/etcd/) != "etcd" ]]; then
    sudo chown etcd: /var/lib/etcd/
fi
