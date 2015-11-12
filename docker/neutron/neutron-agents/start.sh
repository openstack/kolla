#!/bin/bash
set -o errexit

# We must remove all of the stale namespaces if they exist
rm -f /run/netns/*

# Processing /var/lib/kolla/config_files/config.json
python /usr/local/bin/kolla_set_configs

exec /usr/bin/supervisord
