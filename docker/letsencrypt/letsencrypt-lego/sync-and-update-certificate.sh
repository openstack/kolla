#!/bin/bash

function log_info {
    local message="${1}"

    echo "$(date '+%Y/%m/%d %H:%M:%S') [INFO] ${message}"
}

function log_error {
    local message="${1}"

    echo "$(date '+%Y/%m/%d %H:%M:%S') [ERROR] ${message}"
}


# Parser

INTERNAL_SET="false"
EXTERNAL_SET="false"
LOG_FILE="/var/log/kolla/letsencrypt/lesencrypt-lego.log"


VALID_ARGS=$(getopt -o ief:l: --long internal,external,fqdn:,haproxies-ssh: -- "$@")
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
        -f | --fqdn)
            FQDN="${2}"
            shift 2
            ;;
        -l | --haproxies-ssh)
            HAPROXIES_SSH_HOSTS_PORT="${2}"
            shift 2
            ;;
        --) shift;
            break
            ;;
    esac
done

if [ "${INTERNAL_SET}" = "true" ] || [ "${EXTERNAL_SET}" = "true" ]; then
    if [ "${INTERNAL_SET}" = "${EXTERNAL_SET}" ]; then
        log_error "[${FQDN} - hook] Only --internal or --external parameter is allowed at a time"
        exit 1
    fi

    HAPROXIES_SSH_HOSTS_PORT=$(echo ${HAPROXIES_SSH_HOSTS_PORT} | sed -e 's/,/ /g')

    for i in ${HAPROXIES_SSH_HOSTS_PORT}; do

        server=$(echo $i | awk -F ':' '{print $1}')
        port=$(echo $i | awk -F ':' '{print $2}')

        if ! /usr/sbin/ip a | grep -q "${server}"; then

            log_info "[${FQDN} - hook] Rsync lego data /etc/letsencrypt/lego/ to server ${server} and port ${port}"
            rsync -a -e "ssh -p ${port} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityFile=/var/lib/letsencrypt/.ssh/id_rsa" /etc/letsencrypt/lego/ haproxy@${server}:/etc/letsencrypt/lego/ --delete >/dev/null 2>&1
            if [ "$?" -eq 0 ]; then
                log_info "[${FQDN} - hook] Rsync Successful."
            fi

        else
            log_info "[${FQDN} - hook] Rsync lego data /etc/letsencrypt/lego/ to server ${server} and port ${port} not needed."
        fi

        if [ "${INTERNAL_SET}" = "true" ]; then
            internal_cert_path=$(find /etc/letsencrypt/lego/internal/ -name '*.pem')
            sed -i '/^$/d' ${internal_cert_path}
            rsync -av -e "ssh -p ${port} -o StrictHostKeyChecking=no -o IdentityFile=/var/lib/letsencrypt/.ssh/id_rsa" ${internal_cert_path} haproxy@${server}:/var/lib/haproxy/haproxy-internal.pem --delete >/dev/null 2>&1
            ssh -p ${port} -i /var/lib/letsencrypt/.ssh/id_rsa -o StrictHostKeyChecking=no haproxy@${server} "/usr/bin/update-loadbalancer-cert --internal"
        else
            external_cert_path=$(find /etc/letsencrypt/lego/external/ -name '*.pem')
            sed -i '/^$/d' ${external_cert_path}
            rsync -av -e "ssh -p ${port} -o StrictHostKeyChecking=no -o IdentityFile=/var/lib/letsencrypt/.ssh/id_rsa" ${external_cert_path} haproxy@${server}:/var/lib/haproxy/haproxy.pem --delete >/dev/null 2>&1
            ssh -p ${port} -i /var/lib/letsencrypt/.ssh/id_rsa -o StrictHostKeyChecking=no haproxy@${server} "/usr/bin/update-loadbalancer-cert --external"
        fi

    done
fi
