#!/bin/bash -x
#
# This script can be used to start a minimal set of containers that allows
# you to boot an instance.  Note that it requires that you have some openstack
# clients available: keystone, glance, and nova, as well as mysql to ensure
# services are up.  You will also need these in order to interact with the
# installation once started.

setenforce 0

# This should probably go into nova-networking or nova-compute containers.
modprobe ebtables

MY_IP=$(ip route get $(ip route | awk '$1 == "default" {print $3}') |
    awk '$4 == "src" {print $5}')

# Source openrc for commands
source openrc

echo Starting rabbitmq and mariadb
docker-compose -f rabbitmq.yml up -d
docker-compose -f mariadb.yml up -d

until mysql -u root --password=kolla --host=$MY_IP mysql -e "show tables;"
do
    echo waiting for mysql..
    sleep 3
done

echo Starting keystone
docker-compose -f keystone.yml up -d

until keystone user-list
do
    echo waiting for keystone..
    sleep 3
done

echo Starting glance
docker-compose -f glance-api-registry.yml up -d

echo Starting nova
docker-compose -f nova-api-conductor-scheduler.yml up -d

# I think we'll need this..
#
# until mysql -u root --password=kolla --host=$MY_IP mysql -e "use nova;"
# do
#     echo waiting for nova db.
#     sleep 3
# done

echo "Waiting for nova-api to create keystone user.."
until keystone user-list | grep nova
do
    echo waiting for keystone nova user
    sleep 2
done

# This directory is shared with the host to allow qemu instance
# configs to remain accross restarts.
mkdir -p /etc/libvirt/qemu

echo Starting nova compute

docker-compose -f nova-compute-network.yml up -d

IMAGE_URL=http://download.cirros-cloud.net/0.3.3/
IMAGE=cirros-0.3.3-x86_64-disk.img
if ! [ -f "$IMAGE" ]; then
    curl -o $IMAGE $IMAGE_URL/$IMAGE
fi

echo "Creating glance image.."
glance image-create --name "puffy_clouds" --is-public true --disk-format qcow2 --container-format bare --file $IMAGE

# Example usage:
#
# nova secgroup-add-rule default tcp 22 22 0.0.0.0/0
# nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
# nova network-create vmnet --fixed-range-v4=10.0.0.0/24 --bridge=br100 --multi-host=T
#
# nova keypair-add mykey > mykey.pem
# chmod 600 mykey.pem
# nova boot --flavor m1.medium --key_name mykey --image puffy_clouds newInstanceName
