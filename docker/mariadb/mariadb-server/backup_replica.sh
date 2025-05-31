#!/usr/bin/env bash

set -eu
set -o pipefail

BACKUP_DIR=/backup/
DEFAULT_MY_CNF="/etc/mysql/my.cnf"
REPLICA_MY_CNF="$(mktemp)"
RETRY_INTERVAL=5  # Interval between retries (in seconds)
MAX_RETRIES=12    # Max retries (12 retries * 5 seconds = 60 seconds)

# Cleanup function to remove the REPLICA_MY_CNF file
cleanup() {
    rm -f "${REPLICA_MY_CNF}"
}

# Set trap to ensure cleanup occurs on exit or error
trap cleanup EXIT

cd "${BACKUP_DIR}"

# Execute a full backup
backup_full() {
    echo "Taking a full backup"
    LAST_FULL_DATE=$(date +%d-%m-%Y-%s)
    BACKUP_FILE="backup-full-${LAST_FULL_DATE}.mbs.gz"
    BACKUP_PATH="${BACKUP_DIR}/full-${LAST_FULL_DATE}"
    mkdir -p "${BACKUP_PATH}"

    mariabackup \
        --defaults-file="${REPLICA_MY_CNF}" \
        --backup \
        --stream=mbstream \
        --history="${LAST_FULL_DATE}" \
        | gzip > "${BACKUP_PATH}/${BACKUP_FILE}"

    echo "${BACKUP_PATH}/${BACKUP_FILE}" > "${BACKUP_DIR}/last_full_file"
}

# Execute an incremental backup
backup_incremental() {
    if [ ! -r "${BACKUP_DIR}/last_full_file" ]; then
        echo "Error: No full backup file found."
        exit 1
    fi

    FULL_BACKUP_FILE=$(cat "${BACKUP_DIR}/last_full_file")
    LAST_FULL_DATE=$(basename "$(dirname "${FULL_BACKUP_FILE}")" | sed 's/^full-//')
    NOW=$(date +%H-%M-%S-%d-%m-%Y)
    INCR_DIR="${BACKUP_DIR}/incr-${NOW}-since-${LAST_FULL_DATE}"
    mkdir -p "${INCR_DIR}"

    # Temp dir for full base restore
    TMP_BASEDIR=$(mktemp -d)

    echo "Decompressing full backup to temp dir: ${TMP_BASEDIR}"
    gunzip -c "${FULL_BACKUP_FILE}" | mbstream -x -C "${TMP_BASEDIR}"

    mariabackup \
        --defaults-file="${REPLICA_MY_CNF}" \
        --backup \
        --stream=mbstream \
        --incremental-basedir="${TMP_BASEDIR}" \
        --history="incr-${NOW}" \
        | gzip > "${INCR_DIR}/backup-incremental-${NOW}.mbs.gz"

    rm -rf "${TMP_BASEDIR}"
}

# Retry logic for database queries
retry_mysql_query() {
    local query="$1"
    local result=""
    local attempt=1

    while [ ${attempt} -le ${MAX_RETRIES} ]; do
        result=$(mysql -h "${HOST}" -u "${USER}" -p"${PASS}" -s -N -e "${query}" 2>/dev/null || true)
        if [ -n "${result}" ]; then
            echo "${result}"
            return 0
        fi
        echo "Attempt ${attempt}/${MAX_RETRIES} failed. Retrying in ${RETRY_INTERVAL} seconds..."
        sleep "${RETRY_INTERVAL}"
        attempt=$((attempt + 1))
    done

    echo "Error: Failed to execute the query after ${MAX_RETRIES} attempts."
    return 1
}

get_and_set_replica_server() {
    HOST="$(grep '^host' "${DEFAULT_MY_CNF}" | awk -F '=' '{print $2}' | xargs)"
    USER="$(grep '^user' "${DEFAULT_MY_CNF}" | awk -F '=' '{print $2}' | xargs)"
    PASS="$(grep '^password' "${DEFAULT_MY_CNF}" | awk -F '=' '{print $2}' | xargs)"

    ALL_HOSTS_SELECT="SELECT REGEXP_REPLACE(VARIABLE_VALUE, ':[0-9]*','') FROM information_schema.GLOBAL_STATUS WHERE VARIABLE_NAME = 'wsrep_incoming_addresses';"
    ALL_HOSTS=$(retry_mysql_query "${ALL_HOSTS_SELECT}")
    if [ -z "${ALL_HOSTS}" ]; then
        echo "Backup failed due to inability to fetch a list of servers."
        exit 1
    fi

    ACTIVE_HOST_SELECT='SELECT @@hostname;'
    ACTIVE_HOST=$(retry_mysql_query "${ACTIVE_HOST_SELECT}" | xargs getent hosts | awk '{print $1}')
    if [ -z "${ACTIVE_HOST}" ]; then
        echo "Backup failed due to inability to fetch active host."
        exit 1
    fi

    # Multinode
    if echo "${ALL_HOSTS}" | grep -q ','; then
        for server in $(echo "${ALL_HOSTS}" | tr ',' '\n'); do
            if [[ "${server}" != "${ACTIVE_HOST}" ]]; then
                REPLICA_HOST="${server}"
                break
            fi
        done
    # Single node
    else
        REPLICA_HOST="${ALL_HOSTS}"
    fi
    if [ -z "${REPLICA_HOST}" ]; then
        echo "Backup failed due to inability to determine replica host."
        exit 1
    fi

    cp "${DEFAULT_MY_CNF}" "${REPLICA_MY_CNF}"
    sed -i "s/${HOST}/${REPLICA_HOST}/g" "${REPLICA_MY_CNF}"
}

if [ -n "${BACKUP_TYPE}" ]; then
    get_and_set_replica_server
    case "${BACKUP_TYPE}" in
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
