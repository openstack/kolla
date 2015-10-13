#!/bin/bash

set -o xtrace
set -o errexit

sudo mount

# Setup Docker repo and add signing key
echo 'deb http://apt.dockerproject.org/repo ubuntu-trusty main' | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo apt-get update
sudo apt-get install -y --no-install-recommends docker-engine=1.8.2-0~trusty btrfs-tools

# The reason for using BTRFS is stability. There are numerous issues with the
# devicemapper backed on Ubuntu and AUFS is slow. BTRFS is very solid as a
# backend in my experince. I use ie almost exclusively.
# Format Disks and setup Docker to use BTRFS
sudo umount /dev/${DEV} || true
sudo parted /dev/${DEV} -s -- mklabel msdos
sudo service docker stop
echo 'DOCKER_OPTS="-s btrfs"' | sudo tee /etc/default/docker
sudo rm -rf /var/lib/docker/*
sudo mkfs.btrfs -f /dev/${DEV}
sudo mount /dev/${DEV} /var/lib/docker
sudo service docker start

sudo docker info

echo "Completed $0."
