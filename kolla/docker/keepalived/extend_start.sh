#!/bin/bash

# Workaround for bug #1485079
if [ -f /run/keepalived.pid ]; then
    rm /run/keepalived.pid
fi
