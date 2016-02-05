#!/bin/bash

VM=$1
MODE=$2
KOLLA_PATH=$3

REGISTRY=operator.local
REGISTRY_PORT=4000

install_ansible() {
    echo "Installing Ansible"
    apt-get install -y software-properties-common
    apt-add-repository -y ppa:ansible/ansible
    apt-get update
    apt-get install -y ansible=1.9.4*
    cat >/root/.ansible.cfg <<-EOF
[defaults]
forks=100

[ssh_connection]
scp_if_ssh=True
EOF
}

install_docker() {
    echo "Installing Docker"
    apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    echo "deb https://apt.dockerproject.org/repo ubuntu-vivid main" > /etc/apt/sources.list.d/docker.list
    apt-get update
    apt-get install -y docker-engine
    sed -i -r "s,(ExecStart)=(.+),\1=/usr/bin/docker daemon -H fd:// -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --insecure-registry ${REGISTRY}:${REGISTRY_PORT}," /lib/systemd/system/docker.service
    systemctl daemon-reload
    systemctl enable docker
    systemctl restart docker
}

install_python_deps() {
    echo "Installing Python"
    # Python
    apt-get install -y python-setuptools python-dev libffi-dev libssl-dev
    easy_install pip
    pip install --upgrade pip virtualenv virtualenvwrapper
}

install_ntp() {
    echo "Installing NTP"
    # NTP
    apt-get install -y ntp
}

create_registry() {
    echo "Creating Docker Registry"
    docker run -d \
            --name registry \
            --restart=always \
            -p ${REGISTRY_PORT}:5000 \
            -e STANDALONE=True \
            -e MIRROR_SOURCE=https://registry-1.docker.io \
            -e MIRROR_SOURCE_INDEX=https://index.docker.io \
            -e STORAGE_PATH=/var/lib/registry \
            -e GUNICORN_OPTS=[--preload] \
            -e SEARCH_BACKEND=sqlalchemy \
            -v /data/host/registry-storage:/var/lib/registry \
            registry:0.9.1
}

configure_kolla() {
    echo "Configuring Kolla"
    pip install -r ${KOLLA_PATH}/requirements.txt
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

install_ansible
install_docker
install_ntp
install_python_deps
create_registry
configure_kolla

