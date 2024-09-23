#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    SITE_PACKAGES="/var/lib/kolla/venv/lib/python3/site-packages"
    pushd ${SITE_PACKAGES}/skyline_apiserver/db/alembic
    alembic upgrade head
    popd
    exit 0
fi
