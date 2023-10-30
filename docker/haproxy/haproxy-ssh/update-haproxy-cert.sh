#!/bin/bash

function haproxy_transaction_start {
    local cert_input=${1}
    local cert_dest=${2}

    local transaction_result=""
    local transaction_grep_check=""

    transaction_grep_check="Transaction (created|updated) for certificate $(echo $cert_dest | sed -e 's|/|\\/|g')!"
    transaction_result=$(echo -e "set ssl cert ${cert_dest} <<\n$(cat ${cert_input})\n" | socat unix-connect:/var/lib/kolla/haproxy/haproxy.sock -)
    if echo "${transaction_result}" | grep -Pq "${transaction_grep_check}"; then
        echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [INFO] [${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} started."
    else
        echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [ERROR] [${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} failed."
        exit 1
    fi

    local cert_input_sha1=""
    local cert_dest_sha1=""

    cert_input_sha1=$(openssl x509 -noout -fingerprint -sha1 -inform pem -in ${cert_input} | awk -F '=' '{print $2}' | sed -e 's/://g')
    cert_dest_sha1=$(echo "show ssl cert *${cert_dest}" | socat unix-connect:/var/lib/kolla/haproxy/haproxy.sock - | awk -F 'SHA1 FingerPrint: ' '{print $2}' | sed '/^$/d')
    if [ "${cert_input_sha1}" = "${cert_dest_sha1}" ]; then
        echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [INFO] [${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} successfull."
    else
        echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [ERROR] [${cert_dest} - update] Transaction ${cert_input} -> ${cert_dest} failed."
        exit 1
    fi
}

function haproxy_upload_to_memory {
    local cert_input=${1}
    local cert_dest=${2}

    local cert_upload_output=""

    cert_upload_output=$(echo "commit ssl cert ${cert_dest}" | socat unix-connect:/var/lib/kolla/haproxy/haproxy.sock -)
    if echo "${cert_upload_output}" | grep -q "Success!"; then
        echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [INFO] [${cert_dest} - update] Certificate ${cert_input} uploaded to haproxy memory."
    else
        echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [ERROR] [${cert_dest} - update] Certificate ${cert_input} upload to haproxy memory failed."
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
    echo "$(date +%Y/%m-%d) $(date +%H:%M:%S) [INFO] [${cert_haproxy_path} - update] Backuping currently loaded ${cert_haproxy_path} -> /etc/letsencrypt/backups/${cert_backup_name}"
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
