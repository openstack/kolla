#!/bin/bash

set -e

sudo yum install -y libffi-devel openssl-devel docker
sudo /usr/sbin/usermod -a -G dockerroot ${SUDO_USER:-$USER}
sudo systemctl start docker
sleep 1

group_str="jenkins ALL=(:dockerroot) NOPASSWD: ALL"
sudo grep -x "$group_str" /etc/sudoers > /dev/null || sudo bash -c "echo \"$group_str\" >> /etc/sudoers"
sudo chown root:dockerroot /var/run/docker.sock

echo "Completed $0."
