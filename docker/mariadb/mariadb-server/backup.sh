#!/usr/bin/env bash

set -eu
set -o pipefail

# Execute a full backup
backup_full() {
    echo "Taking a full backup"
    mariabackup \
        --defaults-file=/etc/mysql/my.cnf \
        --backup \
        --stream=xbstream \
        --history=$(date +%d-%m-%Y) | gzip > \
        $BACKUP_DIR/mysqlbackup-$(date +%d-%m-%Y-%s).qp.xbc.xbs.gz
}

# Execute an incremental backup
backup_incremental() {
    echo "Taking an incremental backup"
    mariabackup \
        --defaults-file=/etc/mysql/my.cnf \
        --backup \
        --stream=xbstream \
        --incremental-history-name=$(date +%d-%m-%Y) \
        --history=$(date +%d-%m-%Y) | gzip > \
        $BACKUP_DIR/incremental-$(date +%H)-mysqlbackup-$(date +%d-%m-%Y-%s).qp.xbc.xbs.gz
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
