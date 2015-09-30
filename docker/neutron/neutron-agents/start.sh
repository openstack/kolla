#!/bin/bash
set -o errexit

# Processing /opt/kolla/config_files/config.json
python /opt/kolla/set_configs.py

exec /usr/bin/supervisord
