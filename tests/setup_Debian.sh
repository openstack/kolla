#!/bin/bash

set -o xtrace
set -o errexit

DEV=$1

# (SamYaple)TODO: Remove the path overriding
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Setup Docker repo and add signing key
echo 'deb http://apt.dockerproject.org/repo ubuntu-trusty main' | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo apt-get update
sudo apt-get install -y --no-install-recommends docker-engine btrfs-tools

# Only do FS optimization if we have a secondary disk
if [[ -b /dev/${DEV} ]]; then
    # The reason for using BTRFS is stability. There are numerous issues with the
    # devicemapper backed on Ubuntu and AUFS is slow. BTRFS is very solid as a
    # backend in my experince. I use ie almost exclusively.
    # Format Disks and setup Docker to use BTRFS
    sudo umount /dev/${DEV} || true
    sudo parted /dev/${DEV} -s -- mklabel msdos
    sudo service docker stop
    echo 'DOCKER_OPTS="-s btrfs"' | sudo tee /etc/default/docker
    sudo rm -rf /var/lib/docker/*

    # We want to snapshot the entire docker directory so we have to first create a
    # subvolume and use that as the root for the docker directory.
    sudo mkfs.btrfs -f /dev/${DEV}
    sudo mount /dev/${DEV} /var/lib/docker
    sudo btrfs subvolume create /var/lib/docker/docker
    sudo umount /var/lib/docker
    sudo mount -o noatime,compress=lzo,space_cache,subvol=docker /dev/${DEV} /var/lib/docker

    sudo service docker start
fi

sudo docker info

echo "Completed $0."
