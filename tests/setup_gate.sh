#!/bin/bash

set -e

sudo yum install -y libffi-devel openssl-devel
sudo yum install -y http://yum.dockerproject.org/repo/main/fedora/21/Packages/docker-engine-1.7.1-1.fc21.x86_64.rpm
sudo systemctl start docker
sleep 1

group_str="jenkins ALL=(:docker) NOPASSWD: ALL"
sudo grep -x "$group_str" /etc/sudoers > /dev/null || sudo bash -c "echo \"$group_str\" >> /etc/sudoers"

# disable ipv6 until we're sure routes to fedora mirrors work properly
sudo sh -c 'echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf'
sudo /usr/sbin/sysctl -p

echo "Completed $0."
