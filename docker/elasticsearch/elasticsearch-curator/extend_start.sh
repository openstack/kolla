#!/bin/bash

# NOTE(dszumski): Cron runs as root but should be configured to launch Curator
# by the elasticsearch user. Therefore this directory needs to be owned by
# the elasticsearch user.
if [[ ! -d "/var/log/kolla/elasticsearch" ]]; then
    install -d -m 0755 -o elasticsearch -g elasticsearch /var/log/kolla/elasticsearch
fi
