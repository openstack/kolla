#!/bin/bash

set -o errexit

FORCE_GENERATE="${FORCE_GENERATE:-no}"
HASH_PATH=/var/lib/kolla/.settings.md5sum.txt

if [[ ${KOLLA_INSTALL_TYPE} == "binary" ]]; then
    if [[ ${KOLLA_BASE_DISTRO} == "debian" ]] || [[ ${KOLLA_BASE_DISTRO} == "ubuntu" ]]; then
        SITE_PACKAGES="/usr/lib/python3/dist-packages"
    else
        SITE_PACKAGES="/usr/lib/python${KOLLA_DISTRO_PYTHON_VERSION}/site-packages"
    fi
elif [[ ${KOLLA_INSTALL_TYPE} == "source" ]]; then
    SITE_PACKAGES="/var/lib/kolla/venv/lib/python${KOLLA_DISTRO_PYTHON_VERSION}/site-packages"
fi

if [[ -f "/var/lib/kolla/venv/bin/python" ]]; then
    MANAGE_PY="/var/lib/kolla/venv/bin/python /var/lib/kolla/venv/bin/manage.py"
else
    MANAGE_PY="/usr/bin/python${KOLLA_DISTRO_PYTHON_VERSION} /usr/bin/manage.py"
fi

if [[ ${KOLLA_INSTALL_TYPE} == "source" ]] && [[ ! -f ${SITE_PACKAGES}/openstack_dashboard/local/local_settings.py ]]; then
    ln -s /etc/openstack-dashboard/local_settings \
        ${SITE_PACKAGES}/openstack_dashboard/local/local_settings.py
elif [[ ${KOLLA_BASE_DISTRO} == "debian" ]] && [[ ${KOLLA_INSTALL_TYPE} == "binary" ]]; then
    rm -f ${SITE_PACKAGES}/openstack_dashboard/local/local_settings.py
    ln -s /etc/openstack-dashboard/local_settings \
        ${SITE_PACKAGES}/openstack_dashboard/local/local_settings.py
fi

if [[ -f /etc/openstack-dashboard/custom_local_settings ]]; then
    CUSTOM_SETTINGS_FILE="${SITE_PACKAGES}/openstack_dashboard/local/custom_local_settings.py"
    if  [[ ${KOLLA_INSTALL_TYPE} == "binary" ]] && [[ "${KOLLA_BASE_DISTRO}" =~ ubuntu ]]; then
        CUSTOM_SETTINGS_FILE="/usr/share/openstack-dashboard/openstack_dashboard/local/custom_local_settings.py"
    fi

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

function config_freezer_ui {
    for file in ${SITE_PACKAGES}/disaster_recovery/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_FREEZER:-no}" \
            "${SITE_PACKAGES}/disaster_recovery/enabled/${file##*/}" \
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
        "${SITE_PACKAGES}/heat_dashboard/conf/heat_policy.json" \
        "/etc/openstack-dashboard/heat_policy.json"
}

function config_ironic_dashboard {
    for file in ${SITE_PACKAGES}/ironic_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_IRONIC:-no}" \
            "${SITE_PACKAGES}/ironic_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_karbor_dashboard {
    for file in ${SITE_PACKAGES}/karbor_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_KARBOR}" \
            "${SITE_PACKAGES}/karbor_dashboard/enabled/${file##*/}" \
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
}

function config_masakari_dashboard {
    for file in ${SITE_PACKAGES}/masakaridashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MASAKARI:-no}" \
            "${SITE_PACKAGES}/masakaridashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
    config_dashboard "${ENABLE_MASAKARI:-no}"\
        "${SITE_PACKAGES}/masakaridashboard/conf/masakari_policy.json" \
        "/etc/openstack-dashboard/masakari_policy.json"
    config_dashboard "${ENABLE_MASAKARI:-no}"\
        "${SITE_PACKAGES}/masakaridashboard/local/local_settings.d/_50_masakari.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/local_settings.d/_50_masakari.py"
}

function config_monasca_ui {
    config_dashboard "${ENABLE_MONASCA:-no}" \
        "${SITE_PACKAGES}/monitoring/enabled/_50_admin_add_monitoring_panel.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/enabled/_50_admin_add_monitoring_panel.py"
    config_dashboard "${ENABLE_MONASCA:-no}" \
        "${SITE_PACKAGES}/monitoring/conf/monitoring_policy.json" \
        "/etc/openstack-dashboard/monitoring_policy.json"
}

function config_murano_dashboard {
    for file in ${SITE_PACKAGES}/muranodashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MURANO:-no}" \
            "${SITE_PACKAGES}/muranodashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
    config_dashboard "${ENABLE_MURANO:-no}"\
        "${SITE_PACKAGES}/muranodashboard/conf/murano_policy.json" \
        "/etc/openstack-dashboard/murano_policy.json"

    config_dashboard "${ENABLE_MURANO:-no}"\
        "${SITE_PACKAGES}/muranodashboard/local/local_settings.d/_50_murano.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/local_settings.d/_50_murano.py"
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

function config_qinling_dashboard {
    for file in ${SITE_PACKAGES}/qinling_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_QINLING}" \
            "${SITE_PACKAGES}/qinling_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_sahara_dashboard {
    for file in ${SITE_PACKAGES}/sahara_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_SAHARA:-no}" \
            "${SITE_PACKAGES}/sahara_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_searchlight_ui {
    for file in ${SITE_PACKAGES}/searchlight_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_SEARCHLIGHT}" \
            "${SITE_PACKAGES}/searchlight_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_SEARCHLIGHT}" \
        "${SITE_PACKAGES}/searchlight_ui/local_settings.d/_1001_search_settings.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/local_settings.d/_1001_search_settings.py"

    config_dashboard "${ENABLE_SEARCHLIGHT}" \
        "${SITE_PACKAGES}/searchlight_ui/conf/searchlight_policy.json" \
        "/etc/openstack-dashboard/searchlight_policy.json"
}

function config_senlin_dashboard {
    for file in ${SITE_PACKAGES}/senlin_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_SENLIN:-no}" \
            "${SITE_PACKAGES}/senlin_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_SENLIN:-no}" \
        "${SITE_PACKAGES}/senlin_dashboard/conf/senlin_policy.json" \
        "/etc/openstack-dashboard/senlin_policy.json"
}

function config_solum_dashboard {
    for file in ${SITE_PACKAGES}/solumdashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_SOLUM:-no}" \
            "${SITE_PACKAGES}/solumdashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
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

function config_vitrage_dashboard {
    for file in ${SITE_PACKAGES}/vitrage_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_VITRAGE:-no}" \
            "${SITE_PACKAGES}/vitrage_dashboard/enabled/${file##*/}" \
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

function config_zaqar_dashboard {
    for file in ${SITE_PACKAGES}/zaqar_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_ZAQAR:-no}" \
            "${SITE_PACKAGES}/zaqar_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
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
config_freezer_ui
config_heat_dashboard
config_ironic_dashboard
config_karbor_dashboard
config_magnum_dashboard
config_manila_ui
config_masakari_dashboard
config_mistral_dashboard
config_monasca_ui
config_murano_dashboard
config_neutron_vpnaas_dashboard
config_octavia_dashboard
config_qinling_dashboard
config_sahara_dashboard
config_searchlight_ui
config_senlin_dashboard
config_solum_dashboard
config_tacker_dashboard
config_trove_dashboard
config_vitrage_dashboard
config_watcher_dashboard
config_zaqar_dashboard
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

if [[ $(stat -c %a /var/log/kolla/horizon) != "755" ]]; then
    chmod 755 /var/log/kolla/horizon
fi

if [[ -f ${SITE_PACKAGES}/openstack_dashboard/local/.secret_key_store ]] && [[ $(stat -c %U ${SITE_PACKAGES}/openstack_dashboard/local/.secret_key_store) != "horizon" ]]; then
    chown horizon ${SITE_PACKAGES}/openstack_dashboard/local/.secret_key_store
fi

. /usr/local/bin/kolla_httpd_setup

if [[ "${KOLLA_BASE_DISTRO}" == "debian" ]] && [[ ${KOLLA_INSTALL_TYPE} == "binary" ]]; then
    APACHE_RUN_GROUP=horizon
    APACHE_RUN_USER=horizon
fi
