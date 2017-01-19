#!/bin/bash

set -o xtrace
set -o errexit

function setup_disk {
    if [ ! -f /swapfile ]; then
        sudo swapoff -a
        sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
        sudo chmod 0600 /swapfile
        sudo mkswap /swapfile
        sudo /sbin/swapon /swapfile
    fi

    if [ ! -f /docker ]; then
        sudo dd if=/dev/zero of=/docker bs=1M count=20480
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

sudo tee /etc/yum.repos.d/docker.repo << EOF
[docker]
name=Docker Main Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/7
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
EOF

sudo yum -y install libffi-devel openssl-devel docker-engine-1.12.6 docker-engine-selinux-1.12.6 btrfs-progs

setup_disk

# Setup Docker
sudo mkdir /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/kolla.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --storage-driver btrfs --insecure-registry=$(cat /etc/nodepool/primary_node_private):4000
MountFlags=shared
EOF

sudo systemctl daemon-reload

sudo systemctl start docker
sudo docker info

# disable ipv6 until we're sure routes to fedora mirrors work properly
sudo sh -c 'echo "net.ipv6.conf.all.disable_ipv6 = 1" > /etc/sysctl.d/disable_ipv6.conf'
sudo /usr/sbin/sysctl -p

echo "Completed $0."
