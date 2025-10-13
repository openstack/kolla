#!/usr/bin/env bash

set -eu
set -o pipefail

# Execute a full backup
backup_full() {
    echo "Taking a full backup"
    LAST_FULL_DATE=$(date +%d-%m-%Y-%s)
    BACKUP_FILE="mysqlbackup-${LAST_FULL_DATE}.qp.xbc.xbs.gz"
    BACKUP_PATH="$BACKUP_DIR/full-${LAST_FULL_DATE}"
    mkdir -p "$BACKUP_PATH"

    mariabackup \
        --defaults-file=/etc/mysql/my.cnf \
        --backup \
        --stream=xbstream \
        --history=$LAST_FULL_DATE | gzip > \
        "$BACKUP_PATH/$BACKUP_FILE"

    echo "$BACKUP_PATH/$BACKUP_FILE" > "$BACKUP_DIR/last_full_file"
}

# Execute an incremental backup
backup_incremental() {
    echo "Taking an incremental backup"

    if [ ! -r "$BACKUP_DIR/last_full_file" ]; then
        echo "Error: No full backup file found."
        exit 1
    fi

    FULL_BACKUP_FILE=$(cat "$BACKUP_DIR/last_full_file")
    LAST_FULL_DATE=$(basename "$(dirname "$FULL_BACKUP_FILE")" | sed 's/^full-//')
    NOW=$(date +%H-%M-%S-%d-%m-%Y)
    INCR_DIR="$BACKUP_DIR/incr-${NOW}-since-${LAST_FULL_DATE}"
    mkdir -p "$INCR_DIR"

    TMP_BASEDIR=$(mktemp -d)
    echo "Decompressing full backup to temp dir: $TMP_BASEDIR"
    gunzip -c "$FULL_BACKUP_FILE" | mbstream -x -C "$TMP_BASEDIR"

    mariabackup \
        --defaults-file=/etc/mysql/my.cnf \
        --backup \
        --stream=xbstream \
        --incremental-basedir="$TMP_BASEDIR" \
        --history="incr-${NOW}" | gzip > \
        "$INCR_DIR/incremental-${NOW}-mysqlbackup-${LAST_FULL_DATE}.qp.xbc.xbs.gz"

    rm -rf "$TMP_BASEDIR"
}

BACKUP_DIR=/backup/
cd "$BACKUP_DIR"

if [ -n "${BACKUP_TYPE:-}" ]; then
    case "$BACKUP_TYPE" in
        "full")
            backup_full
            ;;
        "incremental")
            backup_incremental
            ;;
        *)
            echo "Only full or incremental options are supported."
            exit 1
            ;;
    esac
else
    echo "You need to specify either full or incremental backup options."
    exit 1
fi
