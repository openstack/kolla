#!/bin/bash

set -o xtrace
set -o errexit

# (SamYaple)TODO: Remove the path overriding
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Setup Docker repo and add signing key
distro_id=$(lsb_release -is)
distro_id=${distro_id,,}
distro_codename=$(lsb_release -cs)

sudo add-apt-repository "deb $DOCKER_REPOS_MIRROR_URL/${distro_id} ${distro_codename} stable"
curl -fsSL $DOCKER_REPOS_MIRROR_URL/${distro_id}/gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install --no-install-recommends docker-ce

sudo docker info

echo "Completed $0."
