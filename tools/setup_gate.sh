#!/bin/bash

set -o xtrace
set -o errexit

# Enable unbuffered output for Ansible in Jenkins.
export PYTHONUNBUFFERED=1

. /etc/ci/mirror_info.sh

function setup_config {

    sudo mkdir -p /etc/kolla

    # Use Infra provided pypi.
    # Wheel package mirror may be not compatible. So do not enable it.
    PIP_CONF=$(mktemp)
    cat > ${PIP_CONF} <<EOF
[global]
timeout = 60
index-url = $NODEPOOL_PYPI_MIRROR
trusted-host = $NODEPOOL_MIRROR_HOST
EOF
    TEMPLATE_OVERRIDES=$(mktemp)

    cat <<EOF | tee "${TEMPLATE_OVERRIDES}"
{% extends parent_template %}

{% block base_header %}

RUN echo $(base64 -w0 "${PIP_CONF}") | base64 -d > /etc/pip.conf

{% if base_distro == 'ubuntu' %}

RUN echo 'APT::Get::AllowUnauthenticated "true";' > /etc/apt/apt.conf.d/99allow-unauthenticated

{% endif %}
{% endblock %}

{% block base_footer %}
{% if base_distro == "centos" %}

RUN sed -i -e "/^mirrorlist/d" \
        -e "s|^#baseurl=http://mirror.centos.org|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/CentOS-Base.repo \
    && sed -i -e "/^mirrorlist/d" \
        -e "s|^#baseurl=http://download.fedoraproject.org/pub|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/epel.repo \
    && sed -i -e "s|^baseurl=http://mirror.centos.org|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/CentOS-Ceph-Jewel.repo

{% elif base_distro == "oraclelinux" %}

RUN sed -i -e "/^mirrorlist/d" \
        -e "s|^#baseurl=http://download.fedoraproject.org/pub|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/epel.repo \
    && sed -i -e "s|^baseurl=http://mirror.centos.org|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/CentOS-Ceph-Jewel.repo

{% elif base_distro == "ubuntu" %}

RUN sed -i -e "s|http://archive.ubuntu.com|http://$NODEPOOL_MIRROR_HOST|" \
        -e "s|http://ubuntu-cloud.archive.canonical.com/ubuntu|http://$NODEPOOL_MIRROR_HOST/ubuntu-cloud-archive|" \
        /etc/apt/sources.list \
    && apt-get update

{% endif %}
{% endblock %}
EOF

cat <<EOF | sudo tee /etc/kolla/kolla-build.conf
[DEFAULT]
# NOTE(Jeffrey4l): use different a docker namespace name in case it pull image from hub.docker.io when deplying
namespace = lokolla
template_override = ${TEMPLATE_OVERRIDES}
registry = 127.0.0.1:4000
push = true
logs_dir = /tmp/logs/build
EOF
}

function setup_registry {

    sudo mkdir /opt/kolla_registry
    sudo chmod -R 644 /opt/kolla_registry
    docker run -d -p 4000:5000 --restart=always -v /opt/kolla_registry/:/var/lib/registry --name registry registry:2
}

setup_registry
setup_config
