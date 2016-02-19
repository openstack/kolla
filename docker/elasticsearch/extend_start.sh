#!/bin/bash

# Only update permissions if permissions need to be updated
if [[ $(stat -c %U:%G /var/lib/elasticsearch/data) != "elasticsearch:elasticsearch" ]]; then
    sudo chown elasticsearch: /var/lib/elasticsearch/data
fi
