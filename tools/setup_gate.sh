#!/bin/bash

set -o xtrace
set -o errexit

# Enable unbuffered output for Ansible in Jenkins.
export PYTHONUNBUFFERED=1

source /etc/nodepool/provider

NODEPOOL_MIRROR_HOST=${NODEPOOL_MIRROR_HOST:-mirror.$NODEPOOL_REGION.$NODEPOOL_CLOUD.openstack.org}
NODEPOOL_MIRROR_HOST=$(echo $NODEPOOL_MIRROR_HOST|tr '[:upper:]' '[:lower:]')
NODEPOOL_PYPI_MIRROR=${NODEPOOL_PYPI_MIRROR:-http://$NODEPOOL_MIRROR_HOST/pypi/simple}

# Just for mandre :)
if [[ ! -f /etc/sudoers.d/jenkins ]]; then
    echo "jenkins ALL=(:docker) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/jenkins
fi

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

{% elif base_distro == "oracle" %}

RUN sed -i -e "/^mirrorlist/d" \
        -e "s|^#baseurl=http://mirror.centos.org|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/oraclelinux-extras.repo \
    && sed -i -e "/^mirrorlist/d" \
        -e "s|^#baseurl=http://download.fedoraproject.org/pub|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/epel.repo \
    && sed -i -e "s|^baseurl=http://mirror.centos.org|baseurl=http://$NODEPOOL_MIRROR_HOST|" \
        /etc/yum.repos.d/CentOS-Ceph-Hammer.repo

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
EOF

}

function detect_distro {
    DISTRO=$(ansible all -i "localhost," -msetup -clocal | awk -F\" '/ansible_os_family/ {print $4}')
}

# NOTE(sdake): This works around broken nodepool on systems with only one
#              private interface
#              The big regex checks for IP addresses in the file
function setup_workaround_broken_nodepool {
    if [[ `grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" /etc/nodepool/node_private | wc -l` -eq 0 ]]; then
        cp /etc/nodepool/node /etc/nodepool/node_private
        cp /etc/nodepool/sub_nodes /etc/nodepool/sub_nodes_private
    fi
}

function setup_ssh {
    # Generate a new keypair that Ansible will use
    ssh-keygen -f /home/jenkins/.ssh/kolla -N ''
    cat /home/jenkins/.ssh/kolla.pub >> /home/jenkins/.ssh/authorized_keys

    # Push the public key around to all of the nodes
    for ip in $(cat /etc/nodepool/sub_nodes_private); do
        scp /home/jenkins/.ssh/kolla.pub ${ip}:/home/jenkins/.ssh/authorized_keys
        # TODO(SamYaple): Remove this root key pushing once Kolla doesn't
        # require root anymore.
        ssh ${ip} -i /home/jenkins/.ssh/kolla 'sudo mkdir -p /root/.ssh; sudo cp /home/jenkins/.ssh/* /root/.ssh/'
    done

    # From now on use the new IdentityFile for connecting to other hosts
    echo "IdentityFile /home/jenkins/.ssh/kolla" >> /home/jenkins/.ssh/config
    chmod 600 /home/jenkins/.ssh/config
}

function setup_inventory {
    local counter=0

    echo -e "127.0.0.1\tlocalhost" > /tmp/hosts
    for ip in $(cat /etc/nodepool/{node_private,sub_nodes_private}); do
        : $((counter++))
        # FIXME(jeffrey4l): do not set two hostnames in oneline. this is a
        # wordround fix for the rabbitmq failed when deploy on CentOS in the CI
        # gate. the ideal fix should set the hostname in setup_gate.sh script.
        # But it do not work as expect with unknown reason
        ssh-keyscan "${ip}" >> ~/.ssh/known_hosts
        echo -e "${ip}\tnode${counter}" >> /tmp/hosts
        echo -e "${ip}\t$(ssh ${ip} hostname)" >> /tmp/hosts
        echo "node${counter}" >> ${RAW_INVENTORY}
    done

    sudo chown root: /tmp/hosts
    sudo chmod 644 /tmp/hosts
    sudo mv /tmp/hosts /etc/hosts
}

function setup_ansible {
    RAW_INVENTORY=/tmp/kolla/raw_inventory
    mkdir /tmp/kolla

    # TODO(SamYaple): Move to virtualenv
    sudo -H pip install -U "ansible>=2" "docker-py>=1.6.0" "python-openstackclient" "python-neutronclient"
    detect_distro

    setup_inventory

    sudo -H pip install ara
    sudo mkdir /etc/ansible
    sudo tee /etc/ansible/ansible.cfg<<EOF
[defaults]
callback_plugins = /usr/lib/python2.7/site-packages/ara/plugins/callbacks:\$VIRTUAL_ENV/lib/python2.7/site-packages/ara/plugins/callbacks
host_key_checking = False
EOF

    # Record the running state of the environment as seen by the setup module
    ansible all -i ${RAW_INVENTORY} -m setup > /tmp/logs/ansible/initial-setup
}

function setup_node {
    ansible-playbook -i ${RAW_INVENTORY} tools/playbook-setup-nodes.yml
}

function setup_logging {
    # This directory is the directory that is copied with the devstack-logs
    # publisher. It must exist at /home/jenkins/workspace/<job-name>/logs
    mkdir logs

    # For ease of access we symlink that logs directory to a known path
    ln -s $(pwd)/logs /tmp/logs
    mkdir -p /tmp/logs/{ansible,build,kolla,kolla_configs,system_logs}
}

function setup_registry {
    sudo mkdir /tmp/kolla_registry
    sudo chmod -R 644 /tmp/kolla_registry
    docker run -d -p 4000:5000 --restart=always -v /tmp/kolla_registry/:/var/lib/registry --name registry registry:2
}

setup_logging
tools/dump_info.sh
setup_workaround_broken_nodepool
setup_ssh
setup_ansible
setup_node
setup_registry
setup_config
