#!/bin/bash

set -o errexit
set -o nounset

# External processes will be occurring and we must wait for them
while [[ ! -e "/kolla_dind_ready" ]]; do
    sleep 1
done

docker daemon -s btrfs 2>&1 > docker.log &
docker_pid=$!

mkdir -p /var/run/sshd
/usr/sbin/sshd -D 2>&1 > sshd.log &
sshd_pid=$!

mkdir -p /root/.ssh/
echo "${SSH_PUB}" > /root/.ssh/authorized_keys

# Wait for docker daemon
sleep 5

# Due to a quirk in the cloning method we end up with a bunch of dead containers
docker rm -v -f $(docker ps -a --no-trunc -q)

# Wait until child processes exit (they should never exit)
wait
