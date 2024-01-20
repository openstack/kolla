#!/bin/bash

function log_info {
    local message="${1}"

    echo "$(date '+%Y/%m/%d %H:%M:%S') [INFO] ${message}"
}

function log_error {
    local message="${1}"

    echo "$(date '+%Y/%m/%d %H:%M:%S') [ERROR] ${message}"
}

function haproxy_transaction_start {
    local cert_input=${1}
    local cert_dest=${2}

    local transaction_result=""
    local transaction_grep_check=""

    transaction_grep_check="Transaction (created|updated) for certificate $(echo $cert_dest | sed -e 's|/|\\/|g')!"
    transaction_result=$(echo -e "set ssl cert ${cert_dest} <<\n$(cat ${cert_input})\n" | socat unix-connect:/var/lib/kolla/haproxy/haproxy.sock -)
    if echo "${transaction_result}" | grep -Pq "${transaction_grep_check}"; then
        log_info "[${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} started."
    else
        log_error "[${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} failed, please check if haproxy admin socket is running and ${cert_input} is not corrupted."
        exit 1
    fi

    local cert_input_sha1=""
    local cert_dest_sha1=""

    cert_input_sha1=$(openssl x509 -noout -fingerprint -sha1 -inform pem -in ${cert_input} | awk -F '=' '{print $2}' | sed -e 's/://g')
    cert_dest_sha1=$(echo "show ssl cert *${cert_dest}" | socat unix-connect:/var/lib/kolla/haproxy/haproxy.sock - | awk -F 'SHA1 FingerPrint: ' '{print $2}' | sed '/^$/d')
    if [ "${cert_input_sha1}" = "${cert_dest_sha1}" ]; then
        log_info "[${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} successful."
    else
        log_error "[${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} failed, SHA1 fingerprint of ${cert_input} is not the same as uploaded one."
        exit 1
    fi
}

function haproxy_upload_to_memory {
    local cert_input=${1}
    local cert_dest=${2}

    local cert_upload_output=""

    cert_upload_output=$(echo "commit ssl cert ${cert_dest}" | socat unix-connect:/var/lib/kolla/haproxy/haproxy.sock -)
    if echo "${cert_upload_output}" | grep -q "Success!"; then
        log_info "[${cert_dest} - update] Certificate ${cert_input} uploaded to haproxy memory."
    else
        log_error "[${cert_dest} - update] Certificate ${cert_input} upload to haproxy memory failed, please check if haproxy admin socket is running and ${cert_input} is not corrupted."
        exit 1
    fi
}

function haproxy_write_to_disk {
    local cert_input=${1}
    local cert_haproxy_path=${2}

    local cert_backup_suffix=""
    local cert_backup_path=""
    local cert_backup_name=""

    cert_backup_suffix="-$(date +%Y-%m-%d-%H-%M-%S).pem"
    cert_backup_path=$(echo "${cert_input}" | awk -v suffix="$cert_backup_suffix" -F '.pem' '{print $1suffix}')
    cert_backup_name=$(echo ${cert_backup_path} | awk -F '/' '{print $NF}')
    mkdir -p /etc/letsencrypt/backups
    log_info "[${cert_haproxy_path} - update] Backuping currently loaded ${cert_haproxy_path} -> /etc/letsencrypt/backups/${cert_backup_name}"
    cp -a ${cert_haproxy_path} /etc/letsencrypt/backups/${cert_backup_name}
    cp -a ${cert_input} ${cert_haproxy_path}
    rm -f ${cert_input}
}


# Parser

INTERNAL_SET="false"
EXTERNAL_SET="false"

VALID_ARGS=$(getopt -o ie --long internal,external -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

eval set -- "$VALID_ARGS"
while [ : ]; do
    case "$1" in
        -i | --internal)
            CERT_TYPE="internal"
            INTERNAL_SET="true"
            shift
            ;;
        -e | --external)
            CERT_TYPE="external"
            EXTERNAL_SET="true"
            shift
            ;;
        --) shift;
            break
            ;;
    esac
done

if [ "${INTERNAL_SET}" = "true" ] || [ "${EXTERNAL_SET}" = "true" ]; then
    if [ "${INTERNAL_SET}" = "${EXTERNAL_SET}" ]; then
        echo "[e] Only --internal or --external parameter is allowed at a time"
        exit 1
    fi
    if [ "${INTERNAL_SET}" = "true" ]; then
        HAPROXY_CERT_INCOMING_PATH="/var/lib/haproxy/haproxy-internal.pem"
        HAPROXY_CERT_PATH="/etc/haproxy/certificates/haproxy-internal.pem"
    else
        HAPROXY_CERT_INCOMING_PATH="/var/lib/haproxy/haproxy.pem"
        HAPROXY_CERT_PATH="/etc/haproxy/certificates/haproxy.pem"
    fi
fi

# Main

haproxy_transaction_start ${HAPROXY_CERT_INCOMING_PATH} ${HAPROXY_CERT_PATH}
haproxy_upload_to_memory ${HAPROXY_CERT_INCOMING_PATH} ${HAPROXY_CERT_PATH}
haproxy_write_to_disk ${HAPROXY_CERT_INCOMING_PATH} ${HAPROXY_CERT_PATH}
