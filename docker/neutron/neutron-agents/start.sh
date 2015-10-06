#!/bin/bash
set -o errexit

# Processing /var/lib/kolla/config_files/config.json
python /usr/local/bin/kolla_set_configs

exec /usr/bin/supervisord
