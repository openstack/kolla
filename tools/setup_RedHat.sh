#!/bin/bash

set -o xtrace
set -o errexit

sudo tee /etc/yum.repos.d/docker-ce-stable.repo << EOF
[docker-ce-stable]
baseurl=$DOCKER_REPOS_MIRROR_URL/centos/7/\$basearch/stable
enabled=1
gpgcheck=1
gpgkey=$DOCKER_REPOS_MIRROR_URL/centos/gpg
module_hotfixes=True
EOF

sudo dnf -y install docker-ce

sudo systemctl start docker
sudo docker info

echo "Completed $0."
