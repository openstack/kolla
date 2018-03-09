#!/usr/bin/env bash

set -eu

# Execute a full backup
backup_full() {
    echo "Taking a full backup"
    innobackupex --defaults-file=/etc/mysql/my.cnf \
        --no-timestamp \
        --stream=xbstream \
        --compress \
        --history=$(date +%d-%m-%Y) ./ > \
        $BACKUP_DIR/mysqlbackup-$(date +%d-%m-%Y-%s).qp.xbc.xbs
}

# Execute an incremental backup
backup_incremental() {
    echo "Taking an incremental backup"
    innobackupex --defaults-file=/etc/mysql/my.cnf \
        --no-timestamp \
        --stream=xbstream \
        --compress \
        --incremental \
        --incremental-history-name=$(date +%d-%m-%Y) \
        --history=$(date +%d-%m-%Y) ./ > \
        $BACKUP_DIR/incremental-$(date +%H)-mysqlbackup-$(date +%d-%m-%Y-%s).qp.xbc.xbs
}

BACKUP_DIR=/backup/
cd $BACKUP_DIR

if [ -n $BACKUP_TYPE ]; then
    case $BACKUP_TYPE in
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

