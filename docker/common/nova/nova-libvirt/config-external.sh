#!/bin/bash
SOURCE=""
TARGET=""
OWNER=""

if [[ -f "$SOURCE" ]]; then
    cp $SOURCE $TARGET
    chown ${OWNER}: $TARGET
    chmod 0644 $TARGET
fi
