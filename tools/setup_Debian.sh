#!/bin/bash

set -o xtrace
set -o errexit

function add_key {
    local counter=0

    while :; do
        if [[ "${counter}" -gt 5 ]]; then
            echo "Failed to add Docker keyring"
            exit 1
        fi
        # hkp://pool.sks-keyservers.net intermittenly doesnt have the correct
        # keyring. p80 is what the docker script pulls from and what we should
        # use for reliability too
        sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D && break || :
        sleep 5
    done
}

function setup_disk {
    if [ ! -f /swapfile ]; then
        sudo swapoff -a
        sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
        sudo chmod 0600 /swapfile
        sudo mkswap /swapfile
        sudo /sbin/swapon /swapfile
    fi

    if [ ! -f /docker ]; then
        sudo dd if=/dev/zero of=/docker bs=1M count=10240
        sudo losetup -f /docker
        DEV=$(losetup -a | awk -F: '/\/docker/ {print $1}')
    fi

    # Format Disks and setup Docker to use BTRFS
    sudo parted ${DEV} -s -- mklabel msdos
    sudo rm -rf /var/lib/docker
    sudo mkdir /var/lib/docker

    # We want to snapshot the entire docker directory so we have to first create a
    # subvolume and use that as the root for the docker directory.
    sudo mkfs.btrfs -f ${DEV}
    sudo mount ${DEV} /var/lib/docker
    sudo btrfs subvolume create /var/lib/docker/docker
    sudo umount /var/lib/docker
    sudo mount -o noatime,subvol=docker ${DEV} /var/lib/docker
}

# (SamYaple)TODO: Remove the path overriding
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

source /etc/lsb-release

# Setup Docker repo and add signing key
echo "deb http://apt.dockerproject.org/repo ubuntu-${DISTRIB_CODENAME} main" | sudo tee /etc/apt/sources.list.d/docker.list
add_key
sudo apt-get update
sudo apt-get -y install --no-install-recommends 'docker-engine=1.12.*'

sudo service docker stop
if [[ ${DISTRIB_CODENAME} == "trusty" ]]; then
    sudo apt-get -y install --no-install-recommends btrfs-tools
    setup_disk
    echo "DOCKER_OPTS=\"-s btrfs --insecure-registry $(cat /etc/nodepool/primary_node_private):4000\"" | sudo tee /etc/default/docker
    sudo mount --make-shared /run
    sudo service docker start
else
    sudo mkdir /etc/systemd/system/docker.service.d
    sudo tee /etc/systemd/system/docker.service.d/kolla.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --storage-driver overlay2 --insecure-registry $(cat /etc/nodepool/primary_node_private):4000
MountFlags=shared
EOF
    sudo systemctl daemon-reload
    sudo systemctl start docker
fi

sudo docker info

echo "Completed $0."
