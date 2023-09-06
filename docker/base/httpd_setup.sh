#!/bin/bash

# This script performs setup necessary to run the Apache httpd web server.
# It should be sourced rather than executed as environment variables are set.

# Assume the service runs on top of Apache httpd when user is root.
if [[ "$(whoami)" == 'root' ]]; then
    # NOTE(pbourke): httpd will not clean up after itself in some cases which
    # results in the container not being able to restart. (bug #1489676, 1557036)
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        # NOTE(yoctozepto): APACHE_CONFDIR has to be set to pass the next step
        # under the `set -o nounset` regime
        APACHE_CONFDIR=
        # Loading Apache2 ENV variables
        . /etc/apache2/envvars
        install -d /var/run/apache2/
        rm -rf /var/run/apache2/*
    else
        rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
        # NOTE(mmalchuk): This added to make Rocky/Centos similar to Ubuntu/Debian
        # to provide /server-status handler for local monitoring of the Apache.
        # The module already loaded in the /etc/httpd/conf.modules.d/00-base.conf.
        cat << EOF >/etc/httpd/conf.modules.d/99-server-status.conf
<Location "/server-status">
    SetHandler server-status
    Require local
</Location>
EOF
    fi

    # CentOS/Rocky have an issue with mod_ssl which produces an invalid Apache
    # configuration in /etc/httpd/conf.d/ssl.conf. This causes the following error
    # on startup:
    #   SSLCertificateFile: file '/etc/pki/tls/certs/localhost.crt' does not exist or is empty
    # Work around this by generating certificates manually.
    # NOTE(mnasiadka): in EL9 upgrade jobs gencerts is failing on wrong permissions to dhparams.pem
    if [[ "${KOLLA_BASE_DISTRO}" =~ centos|rocky ]] && [[ ! -e /etc/pki/tls/certs/localhost.crt ]]; then
        rm -f /tmp/dhparams.pem
        /usr/libexec/httpd-ssl-gencerts
    fi
fi
