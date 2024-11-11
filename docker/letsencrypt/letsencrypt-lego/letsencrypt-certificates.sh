#!/bin/bash

function log_info {
    local message="${1}"

    echo "$(date '+%Y/%m/%d %H:%M:%S') [INFO] ${message}"
}

function log_error {
    local message="${1}"

    echo "$(date '+%Y/%m/%d %H:%M:%S') [ERROR] ${message}"
}

function obtain_or_renew_certificate {
    local certificate_fqdns="${1}"
    local certificate_type="${2}"
    local listen_port="${3}"
    local valid_days="${4}"
    local acme_url="${5}"
    local mail="${6}"
    local letsencrypt_ssh_port="${7}"
    local eab="${8}"
    local hmac="${9}"
    local key_id="${10}"
    local letsencrypt_key_type="${11:-}"

    certificate_domain_opts=$(echo ${certificate_fqdns} | sed -r -e 's/^/,/g' -e 's/,/--domains=/g' -e 's/--/ --/g')
    certificate_fqdn=$(echo ${certificate_fqdns} | awk -F ',' '{print $1}')
    certificate_fqdns=$(echo ${certificate_fqdns} | sed -r 's/,/\ /g')

    if [ -d "/etc/letsencrypt/lego/${certificate_type}/certificates" ]; then
        garbage_count=$(find /etc/letsencrypt/lego/${certificate_type}/certificates/ -type f | grep -v "${certificate_fqdn}" | wc -l)
        if [ ${garbage_count} -ne 0 ]; then
            log_info "[${certificate_fqdn} - cron] Cleaning up garbage in certificates directory."
            find /etc/letsencrypt/lego/${certificate_type}/certificates/ -type f | grep -v "${certificate_fqdn}" | xargs rm -f
        fi
    fi

    if [ -e "/etc/letsencrypt/lego/${certificate_type}/certificates/${certificate_fqdn}.pem" ]; then
        certificate_current_fqdns=$(openssl x509 -text -in /etc/letsencrypt/lego/${certificate_type}/certificates/${certificate_fqdn}.pem \
                                    | grep DNS: \
                                    | sed -r -e 's/\ *DNS://g'  -e 's/^/,/g' -e 's/$/,/g')

        local domains_add=""
        for i in ${certificate_fqdns}; do
            if ! echo "${certificate_current_fqdns}" | grep -q ",${i},"; then
                domains_add="${domains_add} ${i}"
            fi
        done
        domains_add=$(echo "${domains_add}" | sed -r -e 's/^\ //g' -e 's/\ /, /g')

        if [ "${domains_add}" != "" ]; then
            log_info "[${certificate_fqdn} - cron] Domains ${domains_add} will be added to certificate."
            rm -f /etc/letsencrypt/lego/${certificate_type}/certificates/*
        fi
    fi

    [ ! -e "/etc/letsencrypt/lego/${certificate_type}/certificates/${certificate_fqdn}.pem" ] && local lego_action="run" || local lego_action="renew"

    if [ "${eab}" = "true" ]; then
        if [ "${hmac}" != "NONE" ] && [ "${key_id}" != "NONE" ]; then
            eab_opts="--eab --hmac ${hmac} --kid ${key_id}"
        else
            eab_opts=""
            log_error "External Account Binding requires EAB key ID and EAB HMAC key."
            exit 1
        fi
    fi

    log_info "[${certificate_fqdn} - cron] Obtaining certificate for domains ${certificate_fqdns}."
    mapfile -t cmd_output < <(/opt/lego --email="${mail}" \
                                        $( [ -n "${letsencrypt_key_type}" ] && echo "--key-type ${letsencrypt_key_type}" ) \
                                        ${certificate_domain_opts} \
                                        --server "${acme_url}" \
                                        --path "/etc/letsencrypt/lego/${certificate_type}/" \
                                        --http.webroot "/etc/letsencrypt/http-01" \
                                        --http.port ${listen_port} \
                                        --cert.timeout ${valid_days} \
                                        --accept-tos \
                                        --http \
                                        ${eab_opts} \
                                        --pem ${lego_action} \
                                        --${lego_action}-hook="/usr/bin/sync-and-update-certificate --${certificate_type} --fqdn ${certificate_fqdn} --haproxies-ssh ${letsencrypt_ssh_port}" 2>&1)

    # Fix LOG formatting as some output has no same format
    #
    # Example:
    #
    # 2023/10/31 11:52:26 No key found for account michal.arbet@ultimum.io. Generating a P256 key.
    # 2023/10/31 11:52:26 Saved key to /etc/letsencrypt/lego/external/accounts/acme-v02.api.letsencrypt.org/michal.arbet@ultimum.io/keys/michal.arbet@ultimum.io.key
    # 2023/10/31 11:52:27 [INFO] acme: Registering account for michal.arbet@ultimum.io
    # !!!! HEADS UP !!!!

    for i in "${cmd_output[@]}"; do
        if [ "${i}" == "" ]; then
            continue
        fi
        if ! echo "${i}" | grep -q '\[INFO\]'; then
            if [ "$(echo "${i}" | awk -F ' ' '{print $1}')" == "$(date +%Y/%m/%d)" ]; then
                echo "${i}" | awk '{out = ""; for (i = 3; i <= NF; i++) {out = out " " $i}; print $1" "$2" [INFO]"out}'
            else
                dt=$(date '+%Y/%m/%d %H:%M:%S')
                echo "${i}" | awk -v dt="$dt" '{print dt" [INFO] "$0}'
            fi
        else
            echo "${i}"
        fi
    done
}


# Parser

INTERNAL_SET="false"
EXTERNAL_SET="false"
EXTERNAL_ACCOUNT_BINDING="false"
HMAC="NONE"
KEY_ID="NONE"
LOG_FILE="/var/log/kolla/letsencrypt/lesencrypt-lego.log"


VALID_ARGS=$(getopt -o ief:p:d:m:a:v:h:k: --long internal,external,fqdns:,port:,days:,mail:,acme:,vips:,haproxies-ssh:,eab,kid:,hmac:,key-type: -- "$@")
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
        -f | --fqdns)
            FQDNS="${2}"
            shift 2
            ;;
        -p | --port)
            PORT="${2}"
            shift 2
            ;;
        -d | --days)
            DAYS="${2}"
            shift 2
            ;;
        -m | --mail)
            MAIL="${2}"
            shift 2
            ;;
        -a | --acme)
            ACME="${2}"
            shift 2
            ;;
        -v | --vips)
            VIPS="${2}"
            shift 2
            ;;
        -h | --haproxies-ssh)
            LETSENCRYPT_SSH_PORT="${2}"
            shift 2
            ;;
        --eab)
            EXTERNAL_ACCOUNT_BINDING="true"
            shift
            ;;
        --hmac)
            HMAC="${2}"
            shift 2
            ;;
        --kid)
            KEY_ID="${2}"
            shift 2
            ;;
        -k | --key-type)
            LETSENCRYPT_KEY_TYPE="${2}"
            shift 2
            ;;
        --) shift;
            break
            ;;
    esac
done

FQDN=$(echo "${FQDNS}" | awk -F ',' '{print $1}')

if [ "${INTERNAL_SET}" = "true" ] || [ "${EXTERNAL_SET}" = "true" ]; then
    if [ "${INTERNAL_SET}" = "${EXTERNAL_SET}" ]; then
        log_error "[${FQDN} - cron] Only --internal or --external parameter is allowed at a time."
        exit 1
    fi

    LETSENCRYPT_VIP_ADDRESSES="$(echo ${VIPS} | sed -e 's/,/|/g')"
    if [ "${INTERNAL_SET}" = "true" ]; then
        LETSENCRYPT_INTERNAL_FQDNS="${FQDNS}"
    fi

    if [ "${EXTERNAL_SET}" = "true" ]; then
        LETSENCRYPT_EXTERNAL_FQDNS="${FQDNS}"
    fi

    if /usr/sbin/ip a | egrep -q "${LETSENCRYPT_VIP_ADDRESSES}"; then
        log_info "[${FQDN} - cron] This Letsencrypt-lego host is active..."
        if [ "${LETSENCRYPT_INTERNAL_FQDNS}" != "" ]; then
            log_info "[${FQDN} - cron] Processing domains ${LETSENCRYPT_INTERNAL_FQDNS}"
            obtain_or_renew_certificate ${LETSENCRYPT_INTERNAL_FQDNS} internal ${PORT} ${DAYS} ${ACME} ${MAIL} ${LETSENCRYPT_SSH_PORT} ${EXTERNAL_ACCOUNT_BINDING} ${HMAC} ${KEY_ID} ${LETSENCRYPT_KEY_TYPE}
        fi

        if [ "${LETSENCRYPT_EXTERNAL_FQDNS}" != "" ]; then
            log_info "[${FQDN} - cron] Processing domains ${LETSENCRYPT_EXTERNAL_FQDNS}"
            obtain_or_renew_certificate ${LETSENCRYPT_EXTERNAL_FQDNS} external ${PORT} ${DAYS} ${ACME} ${MAIL} ${LETSENCRYPT_SSH_PORT} ${EXTERNAL_ACCOUNT_BINDING} ${HMAC} ${KEY_ID} ${LETSENCRYPT_KEY_TYPE}
        fi
    else
        log_info "[${FQDN} - cron] This Letsencrypt-lego host is passive, nothing to do..."
    fi
fi

if [ -d "/etc/letsencrypt/lego" ]; then
    chown -R haproxy:haproxy /etc/letsencrypt/lego
fi
