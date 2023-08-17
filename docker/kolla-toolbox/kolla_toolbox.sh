#!/usr/bin/env bash

catch_term() {
    exit 0
}

catch_quit() {
    exit 0
}

trap catch_term SIGTERM
trap catch_quit SIGQUIT

while :; do
    sleep 1
done
