#!/bin/bash

set -o errexit

FORCE_GENERATE="${FORCE_GENERATE:-no}"
HASH_PATH=/var/lib/kolla/.settings.md5sum.txt

SITE_PACKAGES="/var/lib/kolla/venv/lib/python3/site-packages"

MANAGE_PY="/var/lib/kolla/venv/bin/python /var/lib/kolla/venv/bin/manage.py"

if [[ ! -f ${SITE_PACKAGES}/openstack_dashboard/local/local_settings.py ]]; then
    ln -s /etc/openstack-dashboard/local_settings \
        ${SITE_PACKAGES}/openstack_dashboard/local/local_settings.py
fi

if [[ -f /etc/openstack-dashboard/custom_local_settings ]]; then
    CUSTOM_SETTINGS_FILE="${SITE_PACKAGES}/openstack_dashboard/local/custom_local_settings.py"

    if [[ ! -L ${CUSTOM_SETTINGS_FILE} ]]; then
        ln -s /etc/openstack-dashboard/custom_local_settings ${CUSTOM_SETTINGS_FILE}
    fi
fi

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    $MANAGE_PY migrate --noinput
    exit 0
fi

function config_dashboard {
    ENABLE=$1
    SRC=$2
    DEST=$3
    if [[ ! -f ${SRC} ]]; then
        echo "WARNING: ${SRC} is required"
    elif [[ "${ENABLE}" == "yes" ]] && [[ ! -f "${DEST}" ]]; then
        cp -a "${SRC}" "${DEST}"
        FORCE_GENERATE="yes"
    elif [[ "${ENABLE}" != "yes" ]] && [[ -f "${DEST}" ]]; then
        # remove pyc pyo files too
        rm -f "${DEST}" "${DEST}c" "${DEST}o"
        FORCE_GENERATE="yes"
    fi
}

function config_blazar_dashboard {
    for file in ${SITE_PACKAGES}/blazar_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_BLAZAR:-no}" \
            "${SITE_PACKAGES}/blazar_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_cloudkitty_dashboard {
    for file in ${SITE_PACKAGES}/cloudkittydashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_CLOUDKITTY:-no}" \
            "${SITE_PACKAGES}/cloudkittydashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_designate_dashboard {
    for file in ${SITE_PACKAGES}/designatedashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_DESIGNATE:-no}" \
            "${SITE_PACKAGES}/designatedashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_fwaas_dashboard {
    for file in ${SITE_PACKAGES}/neutron_fwaas_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_FWAAS:-no}" \
            "${SITE_PACKAGES}/neutron_fwaas_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_heat_dashboard {
    for file in ${SITE_PACKAGES}/heat_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_HEAT:-no}" \
            "${SITE_PACKAGES}/heat_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_HEAT:-no}" \
        "${SITE_PACKAGES}/heat_dashboard/conf/heat_policy.yaml" \
        "/etc/openstack-dashboard/heat_policy.yaml"
    config_dashboard "${ENABLE_HEAT:-no}" \
        "${SITE_PACKAGES}/heat_dashboard/conf/default_policies/heat.yaml" \
        "/etc/openstack-dashboard/default_policies/heat.yaml"
}

function config_ironic_dashboard {
    for file in ${SITE_PACKAGES}/ironic_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_IRONIC:-no}" \
            "${SITE_PACKAGES}/ironic_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_magnum_dashboard {
    for file in ${SITE_PACKAGES}/magnum_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MAGNUM:-no}" \
            "${SITE_PACKAGES}/magnum_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_manila_ui {
    for file in ${SITE_PACKAGES}/manila_ui/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MANILA:-no}" \
            "${SITE_PACKAGES}/manila_ui/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_MANILA:-no}" \
        "${SITE_PACKAGES}/manila_ui/conf/manila_policy.yaml" \
        "/etc/openstack-dashboard/manila_policy.yaml"
    config_dashboard "${ENABLE_MANILA:-no}" \
        "${SITE_PACKAGES}/manila_ui/conf/default_policies/manila.yaml" \
        "/etc/openstack-dashboard/default_policies/manila.yaml"
}

function config_masakari_dashboard {
    for file in ${SITE_PACKAGES}/masakaridashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MASAKARI:-no}" \
            "${SITE_PACKAGES}/masakaridashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
    config_dashboard "${ENABLE_MASAKARI:-no}"\
        "${SITE_PACKAGES}/masakaridashboard/conf/masakari_policy.yaml" \
        "/etc/openstack-dashboard/masakari_policy.yaml"
    config_dashboard "${ENABLE_MASAKARI:-no}"\
        "${SITE_PACKAGES}/masakaridashboard/local/local_settings.d/_50_masakari.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/local_settings.d/_50_masakari.py"
}

function config_mistral_dashboard {
    config_dashboard "${ENABLE_MISTRAL:-no}" \
        "${SITE_PACKAGES}/mistraldashboard/enabled/_50_mistral.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/enabled/_50_mistral.py"
}

function config_neutron_vpnaas_dashboard {
    config_dashboard "${ENABLE_NEUTRON_VPNAAS:-no}" \
        "${SITE_PACKAGES}/neutron_vpnaas_dashboard/enabled/_7100_project_vpn_panel.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/enabled/_7100_project_vpn_panel.py"
}

function config_octavia_dashboard {
    config_dashboard "${ENABLE_OCTAVIA:-no}" \
        "${SITE_PACKAGES}/octavia_dashboard/enabled/_1482_project_load_balancer_panel.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/enabled/_1482_project_load_balancer_panel.py"
}


function config_tacker_dashboard {
    for file in ${SITE_PACKAGES}/tacker_horizon/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_TACKER:-no}" \
            "${SITE_PACKAGES}/tacker_horizon/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_trove_dashboard {
    for file in ${SITE_PACKAGES}/trove_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_TROVE:-no}" \
            "${SITE_PACKAGES}/trove_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_watcher_dashboard {
    for file in ${SITE_PACKAGES}/watcher_dashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_WATCHER:-no}" \
            "${SITE_PACKAGES}/watcher_dashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_WATCHER:-no}" \
            "${SITE_PACKAGES}/watcher_dashboard/conf/watcher_policy.json" \
            "/etc/openstack-dashboard/watcher_policy.json"
}

function config_zun_dashboard {
    for file in ${SITE_PACKAGES}/zun_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_ZUN:-no}" \
            "${SITE_PACKAGES}/zun_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

# Regenerate the compressed javascript and css if any configuration files have
# changed.  Use a static modification date when generating the tarball
# so that we only trigger on content changes.
function settings_bundle {
    # NOTE(yoctozepto): We ignore errors here (|| true) to make it work with
    # `set -o pipefail` (files might be missing - no problem).
    tar -cf- --mtime=1970-01-01 \
        /etc/openstack-dashboard/local_settings \
        /etc/openstack-dashboard/custom_local_settings \
        /etc/openstack-dashboard/local_settings.d 2> /dev/null || true
}

function settings_changed {
    changed=1

    if [[ ! -f $HASH_PATH  ]] || ! settings_bundle | md5sum -c --status $HASH_PATH || [[ $FORCE_GENERATE == yes ]]; then
        changed=0
    fi

    return ${changed}
}

config_blazar_dashboard
config_cloudkitty_dashboard
config_designate_dashboard
config_fwaas_dashboard
config_heat_dashboard
config_ironic_dashboard
config_magnum_dashboard
config_manila_ui
config_masakari_dashboard
config_mistral_dashboard
config_neutron_vpnaas_dashboard
config_octavia_dashboard
config_tacker_dashboard
config_trove_dashboard
config_watcher_dashboard
config_zun_dashboard

if settings_changed; then
    ${MANAGE_PY} collectstatic --noinput --clear
    ${MANAGE_PY} compress --force
    settings_bundle | md5sum > $HASH_PATH
fi

# NOTE(sbezverk) since Horizon is now storing logs in its own location, /var/log/horizon
# needs to be created if it does not exist
if [[ ! -d "/var/log/kolla/horizon" ]]; then
    mkdir -p /var/log/kolla/horizon
fi

if [[ $(stat -c %U:%G /var/log/kolla/horizon) != "horizon:kolla" ]]; then
    chown -R horizon:kolla /var/log/kolla/horizon
fi

if [[ $(stat -c %a /var/log/kolla/horizon) != "755" ]]; then
    chmod 755 /var/log/kolla/horizon
fi

if [[ -f ${SITE_PACKAGES}/openstack_dashboard/local/.secret_key_store ]] && [[ $(stat -c %U ${SITE_PACKAGES}/openstack_dashboard/local/.secret_key_store) != "horizon" ]]; then
    chown horizon ${SITE_PACKAGES}/openstack_dashboard/local/.secret_key_store
fi

. /usr/local/bin/kolla_httpd_setup
