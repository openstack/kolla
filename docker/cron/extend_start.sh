#!/bin/bash

CRON_LOGROTATE_CURRENT_PATH="$(find /etc/cron* -name logrotate)"
CRON_LOGROTATE_CURRENT_SCHEDULE=$(echo "${CRON_LOGROTATE_CURRENT_PATH}" | sed -r 's/(.*)(hourly|daily|weekly|monthly)(.*)/\2/g')

if [ -z $CRON_LOGROTATE_CURRENT_PATH ]; then
    echo "logrotate is not handled by cron"
else
    # Pass only for hourly|daily|weekly|monthly
    if [[ "${KOLLA_LOGROTATE_SCHEDULE:-undefined}" =~ hourly|daily|weekly|monthly ]]; then

        CRON_LOGROTATE_DESIRED_PATH="/etc/cron.${KOLLA_LOGROTATE_SCHEDULE}/logrotate"

        if [[ "${CRON_LOGROTATE_CURRENT_PATH}" != "${CRON_LOGROTATE_DESIRED_PATH}" ]]; then
            mv ${CRON_LOGROTATE_CURRENT_PATH} ${CRON_LOGROTATE_DESIRED_PATH}
            CRON_LOGROTATE_CURRENT_SCHEDULE="${KOLLA_LOGROTATE_SCHEDULE}"
        fi
    fi

    echo "[i] Cron schedule for logrotate is currently set to: ${CRON_LOGROTATE_CURRENT_SCHEDULE}."
fi
