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

sudo yum -y install docker-ce

# Disable SELinux
setenforce 0

sudo systemctl start docker
sudo docker info

echo "Completed $0."
