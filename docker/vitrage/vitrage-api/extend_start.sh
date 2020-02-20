#!/bin/bash

if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    vitrage-dbsync
    exit 0
fi

. /usr/local/bin/kolla_httpd_setup
