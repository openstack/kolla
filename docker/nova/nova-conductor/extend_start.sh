#!/bin/bash

if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    nova-manage db sync
    nova-manage db online_data_migrations
    exit 0
fi

if [[ "${!KOLLA_UPGRADE[@]}" ]]; then
    nova-manage db sync
    exit 0
fi

if [[ "${!KOLLA_OSM[@]}" ]]; then
    nova-manage db online_data_migrations
    exit 0
fi
