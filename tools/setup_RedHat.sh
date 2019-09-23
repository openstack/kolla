#!/bin/bash

set -o xtrace
set -o errexit

# (SamYaple)TODO: Remove the path overriding
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

sudo tee /etc/yum.repos.d/docker-ce-stable.repo << EOF
[docker-ce-stable]
baseurl=$DOCKER_REPOS_MIRROR_URL/centos/7/\$basearch/stable
enabled=1
gpgcheck=1
gpgkey=$DOCKER_REPOS_MIRROR_URL/centos/gpg
EOF

sudo yum -y install libffi-devel openssl-devel docker-ce btrfs-progs

# Disable SELinux
setenforce 0

# Setup Docker
sudo mkdir /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/kolla.conf << EOF
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --storage-driver overlay2 --insecure-registry=0.0.0.0/0
MountFlags=shared
EOF

sudo systemctl daemon-reload

sudo systemctl start docker
sudo docker info

# disable ipv6 until we're sure routes to fedora mirrors work properly
sudo sh -c 'echo "net.ipv6.conf.all.disable_ipv6 = 1" > /etc/sysctl.d/disable_ipv6.conf'
sudo /usr/sbin/sysctl -p

echo "Completed $0."
