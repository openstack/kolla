#!/bin/bash

# This script finds all projects in /dev-mode folder and
# installs them using pip
# The projects are mounted there when dev mode is enabled for them
# in kolla-ansible

if [ -d "/dev-mode" ]; then
    for project in /dev-mode/*; do
        pip install -U "$project"
    done
fi
