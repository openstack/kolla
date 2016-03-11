#!/bin/bash
#
# Bootstrap script to configure all nodes.
#

VM=$1
MODE=$2
KOLLA_PATH=$3

export http_proxy=
export https_proxy=

if [ "$MODE" = 'aio' ]; then
    # Run registry on port 4000 since it may collide with keystone when doing AIO
    REGISTRY_PORT=4000
    SUPPORT_NODE=operator
else
    REGISTRY_PORT=5000
    SUPPORT_NODE=support01
fi
REGISTRY=operator.local:${REGISTRY_PORT}
ADMIN_PROTOCOL="http"

# Install common packages and do some prepwork.
function prep_work {
    apt-get update
    apt-get install -y python-mysqldb python-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt-dev
    apt-get clean
    easy_install pip
    pip install --upgrade docker-py
}

# Install and configure a quick&dirty docker daemon.
function install_docker {
    # Allow for an externally supplied docker binary.
    if [[ -f "/data/docker" ]]; then
        cp /vagrant/docker /usr/bin/docker
        chmod +x /usr/bin/docker
    else
        apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
        echo "deb https://apt.dockerproject.org/repo ubuntu-wily main" > /etc/apt/sources.list.d/docker.list
        apt-get update
        apt-get install -y docker-engine
        sed -i -r "s,(ExecStart)=(.+),\1=/usr/bin/docker daemon --insecure-registry ${REGISTRY} --registry-mirror=http://${REGISTRY}|" /lib/systemd/system/docker.service
        systemctl daemon-reload
        systemctl enable docker
        systemctl restart docker
    fi
}

function configure_kolla {
    # Use local docker registry
    sed -i -r "s,^[# ]*namespace *=.+$,namespace = ${REGISTRY}/lokolla," /etc/kolla/kolla-build.conf
    sed -i -r "s,^[# ]*push *=.+$,push = True," /etc/kolla/kolla-build.conf
    sed -i -r "s,^[# ]*docker_registry:.+$,docker_registry: \"${REGISTRY}\"," /etc/kolla/globals.yml
    sed -i -r "s,^[# ]*docker_namespace:.+$,docker_namespace: \"lokolla\"," /etc/kolla/globals.yml
    sed -i -r "s,^[# ]*docker_insecure_registry:.+$,docker_insecure_registry: \"True\"," /etc/kolla/globals.yml
    # Set network interfaces
    sed -i -r "s,^[# ]*network_interface:.+$,network_interface: \"eth1\"," /etc/kolla/globals.yml
    sed -i -r "s,^[# ]*neutron_external_interface:.+$,neutron_external_interface: \"eth2\"," /etc/kolla/globals.yml
}

# Configure the operator node and install some additional packages.
function configure_operator {
    apt-get install -y git mariadb-client selinux-utils && apt-get clean
    pip install --upgrade "ansible<2" python-openstackclient python-neutronclient tox

    pip install ~vagrant/kolla

    # Note: this trickery requires a patched docker binary.
    if [[ "$http_proxy" = "" ]]; then
        su - vagrant sh -c "echo BUILDFLAGS=\\\"--build-env=http_proxy=$http_proxy --build-env=https_proxy=$https_proxy\\\" > ~/kolla/.buildconf"
    fi

    cp -r ~vagrant/kolla/etc/kolla/ /etc/kolla
    oslo-config-generator --config-file \
        ~vagrant/kolla/etc/oslo-config-generator/kolla-build.conf \
        --output-file /etc/kolla/kolla-build.conf
    mkdir -p /usr/share/kolla
    chown -R vagrant: /etc/kolla /usr/share/kolla

    configure_kolla

    # Make sure Ansible uses scp.
    cat > ~vagrant/.ansible.cfg <<EOF
[defaults]
forks=100

[ssh_connection]
scp_if_ssh=True
EOF
    chown vagrant: ~vagrant/.ansible.cfg

    mkdir -p /etc/kolla/config/nova/
    cat > /etc/kolla/config/nova/nova-compute.conf <<EOF
[libvirt]
virt_type=qemu
EOF


    # Launch a local registry (and mirror) to speed up pulling images.
    if [[ ! $(docker ps -a -q -f name=registry) ]]; then
        docker run -d \
            --name registry \
            --restart=always \
            -p ${REGISTRY_PORT}:5000 \
            -e STANDALONE=True \
            -e MIRROR_SOURCE=https://registry-1.docker.io \
            -e MIRROR_SOURCE_INDEX=https://index.docker.io \
            -e STORAGE_PATH=/var/lib/registry \
            -v /data/host/registry-storage:/var/lib/registry \
            registry:2
    fi
}

echo "Kernel version $(uname -r)"
if [[ $(uname -r) != *"4.2"* ]]; then
    echo "Going to update kernel image"
    apt-get update
    apt-get install -y linux-image-generic-lts-wily
    # VM needs to be rebooted for docker to pickup the changes
    echo "Rebooting for kernel changes"
    echo "After reboot re-run vagrant provision to finish provising the box"
    reboot
    # Sleep for a bit to let vagrant exit properly
    sleep 3
fi

prep_work
install_docker

if [[ "$VM" = "operator" ]]; then
    configure_operator
fi
