#!/bin/bash

# Copying configs into place if needed and set run command
python /opt/kolla/set_configs.py
CMD=$(cat /run_command)
