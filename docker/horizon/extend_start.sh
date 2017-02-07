#!/bin/bash

set -o errexit

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    MANAGE_PY="/usr/bin/python /usr/bin/manage.py"
    if [[ -f "/var/lib/kolla/venv/bin/python" ]]; then
        MANAGE_PY="/var/lib/kolla/venv/bin/python /var/lib/kolla/venv/bin/manage.py"
    fi
    $MANAGE_PY migrate --noinput
    exit 0
fi

FORCE_GENERATE="no"

if [[ ${KOLLA_INSTALL_TYPE} == "binary" ]]; then
    SITE_PACKAGES="/usr/lib/python2.7/site-packages"
elif [[ ${KOLLA_INSTALL_TYPE} == "source" ]]; then
    SITE_PACKAGES="/var/lib/kolla/venv/lib/python2.7/site-packages"
fi

function config_dashboard {
    ENABLE=$1
    SRC=$2
    DEST=$3
    if [[ "${ENABLE}" == "yes" ]] && [[ ! -f "${DEST}" ]]; then
        cp -a "${SRC}" "${DEST}"
        FORCE_GENERATE="yes"
    elif [[ "${ENABLE}" != "yes" ]] && [[ -f "${DEST}" ]]; then
        # remove pyc pyo files too
        rm -f "${DEST}" "${DEST}c" "${DEST}o"
        FORCE_GENERATE="yes"
    fi
}

function config_cloudkitty_dashboard {
    for file in ${SITE_PACKAGES}/cloudkittydashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_CLOUDKITTY}" \
            "${SITE_PACKAGES}/cloudkittydashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_designate_dashboard {
    for file in ${SITE_PACKAGES}/designatedashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_DESIGNATE}" \
            "${SITE_PACKAGES}/designatedashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_freezer_ui {
    for file in ${SITE_PACKAGES}/disaster_recovery/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_FREEZER}" \
            "${SITE_PACKAGES}/disaster_recovery/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_ironic_dashboard {
    for file in ${SITE_PACKAGES}/ironic_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_IRONIC}" \
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
        config_dashboard "${ENABLE_MAGNUM}" \
            "${SITE_PACKAGES}/magnum_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_manila_ui {
    for file in ${SITE_PACKAGES}/manila_ui/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MANILA}" \
            "${SITE_PACKAGES}/manila_ui/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_murano_dashboard {
    for file in ${SITE_PACKAGES}/muranodashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_MURANO}" \
            "${SITE_PACKAGES}/muranodashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
    config_dashboard "${ENABLE_MURANO}"\
        "${SITE_PACKAGES}/muranodashboard/conf/murano_policy.json" \
        "/etc/openstack-dashboard/murano_policy.json"

    config_dashboard "${ENABLE_MURANO}"\
        "${SITE_PACKAGES}/muranodashboard/local/local_settings.d/_50_murano.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/local_settings.d/_50_murano.py"
}

function config_mistral_dashboard {
    config_dashboard "${ENABLE_MISTRAL}" \
        "${SITE_PACKAGES}/mistraldashboard/enabled/_50_mistral.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/enabled/_50_mistral.py"
}

function config_neutron_lbaas {
    config_dashboard "${ENABLE_NEUTRON_LBAAS}" \
        "${SITE_PACKAGES}/neutron_lbaas_dashboard/enabled/_1481_project_ng_loadbalancersv2_panel.py" \
        "${SITE_PACKAGES}/openstack_dashboard/local/enabled/_1481_project_ng_loadbalancersv2_panel.py"
}

function config_sahara_dashboard {
    for file in ${SITE_PACKAGES}/sahara_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_SAHARA}" \
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
        config_dashboard "${ENABLE_SENLIN}" \
            "${SITE_PACKAGES}/senlin_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_SENLIN}" \
        "${SITE_PACKAGES}/senlin_dashboard/conf/senlin_policy.json" \
        "/etc/openstack-dashboard/senlin_policy.json"
}

function config_solum_dashboard {
    for file in ${SITE_PACKAGES}/solumdashboard/local/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_SOLUM}" \
            "${SITE_PACKAGES}/solumdashboard/local/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_tacker_dashboard {
    for file in ${SITE_PACKAGES}/tacker_horizon/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_TACKER}" \
            "${SITE_PACKAGES}/tacker_horizon/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_trove_dashboard {
    for file in ${SITE_PACKAGES}/trove_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_TROVE}" \
            "${SITE_PACKAGES}/trove_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function config_watcher_dashboard {
    for file in ${SITE_PACKAGES}/watcher_dashboard/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_WATCHER}" \
            "${SITE_PACKAGES}/watcher_dashboard/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done

    config_dashboard "${ENABLE_WATCHER}" \
            "${SITE_PACKAGES}/watcher_dashboard/conf/watcher_policy.json" \
            "/etc/openstack-dashboard/watcher_policy.json"
}

function config_zaqar_dashboard {
    for file in ${SITE_PACKAGES}/zaqar_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_ZAQAR}" \
            "${SITE_PACKAGES}/zaqar_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

config_cloudkitty_dashboard
config_designate_dashboard
config_freezer_ui
config_ironic_dashboard
config_karbor_dashboard
config_magnum_dashboard
config_manila_ui
config_mistral_dashboard
config_murano_dashboard
config_neutron_lbaas
config_sahara_dashboard
config_searchlight_ui
config_senlin_dashboard
config_solum_dashboard
config_tacker_dashboard
config_trove_dashboard
config_watcher_dashboard
config_zaqar_dashboard

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. (bug #1489676, 1557036)
if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    . /etc/apache2/envvars
    rm -rf /var/run/apache2/*
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
fi

# NOTE(jeffrey4l): The local_settings file affect django-compress
# behavior, so re-generate the compressed javascript and css if it
# is changed
MD5SUM_TXT_PATH="/tmp/.local_settings.md5sum.txt"
if [[ ! -f ${MD5SUM_TXT_PATH} || $(md5sum -c --status ${MD5SUM_TXT_PATH};echo $?) != 0 || ${FORCE_GENERATE} == "yes" ]]; then
    md5sum /etc/openstack-dashboard/local_settings > ${MD5SUM_TXT_PATH}
    if [[ "${KOLLA_INSTALL_TYPE}" == "binary" ]]; then
        /usr/bin/manage.py collectstatic --noinput --clear
        /usr/bin/manage.py compress --force
    elif [[ "${KOLLA_INSTALL_TYPE}" == "source" ]]; then
        /var/lib/kolla/venv/bin/python /var/lib/kolla/venv/bin/manage.py collectstatic --noinput --clear
        /var/lib/kolla/venv/bin/python /var/lib/kolla/venv/bin/manage.py compress --force
    fi
fi

# NOTE(sbezverk) since Horizon is now storing logs in its own location, /var/log/horizon
# needs to be created if it does not exist
if [[ ! -d "/var/log/kolla/horizon" ]]; then
    mkdir -p /var/log/kolla/horizon
fi
if [[ $(stat -c %a /var/log/kolla/horizon) != "755" ]]; then
    chmod 755 /var/log/kolla/horizon
fi
