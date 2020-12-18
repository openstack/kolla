#!/usr/bin/env bash

set -eu
set -o pipefail

# Execute a full backup
backup_full() {
    echo "Taking a full backup"
    LAST_FULL_DATE=$(date +%d-%m-%Y)
    mariabackup \
        --defaults-file=/etc/mysql/my.cnf \
        --backup \
        --stream=xbstream \
        --history=$LAST_FULL_DATE | gzip > \
        $BACKUP_DIR/mysqlbackup-$(date +%d-%m-%Y-%s).qp.xbc.xbs.gz
    echo $LAST_FULL_DATE > $BACKUP_DIR/last_full_date
}

# Execute an incremental backup
backup_incremental() {
    echo "Taking an incremental backup"
    if [ -r $BACKUP_DIR/last_full_date ]; then
        LAST_FULL_DATE=$(cat $BACKUP_DIR/last_full_date)
    fi
    if [ -z $LAST_FULL_DATE ]; then
        LAST_FULL_DATE=$(date +%d-%m-%Y)
    fi
    mariabackup \
        --defaults-file=/etc/mysql/my.cnf \
        --backup \
        --stream=xbstream \
        --incremental-history-name=$LAST_FULL_DATE \
        --history=$LAST_FULL_DATE | gzip > \
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
