#!/bin/bash

set -o xtrace
set -o errexit

function setup_disk {
    if [[ -f /etc/nodepool/provider && ! -f /swapfile ]]; then
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

# Excerpts from https://github.com/openstack-infra/devstack-gate/blob/dc49f9e6eb18e42c6b175e4e146fa8f3b7633279/functions.sh#L306
    if [ -b /dev/xvde ]; then
        DEV2='/dev/xvde'
        if mount | grep ${DEV2} > /dev/null; then
            echo "*** ${DEV2} appears to already be mounted"
            echo "*** ${DEV2} unmounting and reformating"
            sudo umount ${DEV2}
        fi
        sudo parted ${DEV2} --script -- mklabel msdos
        sync
        sudo partprobe
        sudo mkfs.ext4 ${DEV2}
        sudo mount ${DEV2} /mnt
        sudo find /opt/ -mindepth 1 -maxdepth 1 -exec mv {} /mnt/ \;
        sudo umount /mnt
        sudo mount ${DEV2} /opt
        grep -q ${DEV2} /proc/mounts || exit 1
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

. /etc/lsb-release

# Setup Docker repo and add signing key
sudo apt-get update
sudo apt-get -y install apt-transport-https
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install --no-install-recommends docker-ce

sudo service docker stop
if [[ ${DISTRIB_CODENAME} == "trusty" ]]; then
    sudo apt-get -y install --no-install-recommends btrfs-tools
    setup_disk
    echo "DOCKER_OPTS=\"-s btrfs --insecure-registry 0.0.0.0/0\"" | sudo tee /etc/default/docker
    sudo mount --make-shared /run
    sudo service docker start
else
    sudo mkdir /etc/systemd/system/docker.service.d
    sudo tee /etc/systemd/system/docker.service.d/kolla.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --storage-driver overlay2 --insecure-registry 0.0.0.0/0
MountFlags=shared
EOF
    sudo systemctl daemon-reload
    sudo systemctl start docker
fi

sudo docker info

echo "Completed $0."
