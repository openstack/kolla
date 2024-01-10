#!/usr/bin/env bash

catch_term() {
    ovs-appctl -T1 -t /run/openvswitch/$1.$child.ctl exit
    exit 0
}

catch_quit() {
    ovs-appctl -T1 -t /run/openvswitch/$1.$child.ctl exit
    exit 0
}

trap catch_term SIGTERM
trap catch_quit SIGQUIT

"$@" &

child=$!
wait "$child"
