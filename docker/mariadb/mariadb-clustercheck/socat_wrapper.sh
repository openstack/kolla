#!/usr/bin/env bash

catch_term() {
    kill -TERM "$child" 2>/dev/null
    exit 0
}

catch_quit() {
    kill -QUIT "$child" 2>/dev/null
    exit 0
}

trap catch_term SIGTERM
trap catch_quit SIGQUIT

socat "$@" &

child=$!
wait "$child"
