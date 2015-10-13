#!/bin/bash

set -o xtrace
set -o errexit

cat | sudo tee /etc/yum.repos.d/docker.repo << EOF
[docker]
name=Docker Main Repository
baseurl=https://yum.dockerproject.org/repo/main/fedora/21
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
EOF

sudo yum install -y libffi-devel openssl-devel docker-engine-1.8.2 xfsprogs

# Setup backing disk for use with Docker. This is to ensure we use the ephemeral
# disk provided to the build instance. It ensures the correct disk and storage
# driver are used for Docker. It is recommend to use the thin provisioning
# driver. https://github.com/docker/docker/blob/master/man/docker.1.md
sudo parted /dev/${DEV} -s -- mklabel msdos mkpart pri 1 -1
sudo pvcreate /dev/${DEV}1
sudo vgcreate kolla01 /dev/${DEV}1
sudo lvcreate -n thin01 -L 60G kolla01
sudo lvcreate -n thin01meta -L 2G kolla01
yes | sudo lvconvert --type thin-pool --poolmetadata kolla01/thin01meta kolla01/thin01

# Setup Docker
sudo sed -i -r 's,(ExecStart)=(.+),\1=/usr/bin/docker daemon --storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=kolla01-thin01 --storage-opt dm.use_deferred_removal=true,' /usr/lib/systemd/system/docker.service
sudo systemctl daemon-reload
sudo systemctl start docker
sudo docker info

# disable ipv6 until we're sure routes to fedora mirrors work properly
sudo sh -c 'echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf'
sudo /usr/sbin/sysctl -p

echo "Completed $0."
