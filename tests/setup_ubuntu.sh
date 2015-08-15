#!/bin/bash

set -o xtrace
set -o errexit

# Setup Docker repo and add signing key
echo 'deb http://apt.dockerproject.org/repo ubuntu-trusty main' | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo apt-get update
sudo apt-get install -y --no-install-recommends docker-engine btrfs-progs

# We break the gate initially since it will not function until i can test against the ubuntu gate
exit 1

echo "Completed $0."
