Swift in Kolla
==============

Overview
--------
Kolla can deploy a full working Swift setup in either a AIO or multi node setup.

Prerequisites
-------------
Before running Swift we need to generate "rings", which are binary compressed files that at a high
level let the various Swift services know where data is in the cluster. We hope to automate this
process in a future release.

Swift also expects block devices to be available and partitioned on the host, which Swift uses in
combination with the rings to store data. Swift demos commonly just use directories created under
/srv/node to simulate these devices. In order to ease "out of the box" testing of Kolla, we offer a
similar setup with a data container. *Note*, data containers are very inefficient for this purpose.
In production setups operators will want to provision disks according to the Swift operator guide,
which can then be added the rings and used in Kolla.

For an AIO setup, the following commands can be used, locally, to generate rings containing the data
container directories:

::

  export KOLLA_INTERNAL_ADDRESS=1.2.3.4
  export KOLLA_BASE_DISTRO=centos
  export KOLLA_INSTALL_TYPE=binary

  # Object ring
  docker run \
    -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
    kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base \
    swift-ring-builder /etc/kolla/config/swift/object.builder create 10 3 1

  for partition in sdb1 sdb2 sdb3; do
    docker run \
      -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
      kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base swift-ring-builder \
      /etc/kolla/config/swift/object.builder add z1-${KOLLA_INTERNAL_ADDRESS}:6000/${partition} 1;
  done

  # Account ring
  docker run \
    -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
    kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base \
    swift-ring-builder /etc/kolla/config/swift/account.builder create 10 3 1

  for partition in sdb1 sdb2 sdb3; do
    docker run \
      -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
      kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base swift-ring-builder \
      /etc/kolla/config/swift/account.builder add z1-${KOLLA_INTERNAL_ADDRESS}:6001/${partition} 1;
  done

  # Container ring
  docker run \
    -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
    kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base \
    swift-ring-builder /etc/kolla/config/swift/container.builder create 10 3 1

  for partition in sdb1 sdb2 sdb3; do
    docker run \
      -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
      kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base swift-ring-builder \
      /etc/kolla/config/swift/container.builder add z1-${KOLLA_INTERNAL_ADDRESS}:6002/${partition} 1;
  done

  for ring in object account container; do
    docker run \
      -v /etc/kolla/config/swift/:/etc/kolla/config/swift/ \
      kollaglue/${KOLLA_BASE_DISTRO}-${KOLLA_INSTALL_TYPE}-swift-base swift-ring-builder \
      /etc/kolla/config/swift/${ring}.builder rebalance;
  done

Similar commands can be used for multinode, you will just need to run the the 'add' step for each IP
in the cluster.

For more info, see
http://docs.openstack.org/kilo/install-guide/install/apt/content/swift-initial-rings.html

Deploying
---------
Once the rings are in place, deploying Swift is the same as any other Kolla Ansible service. Below
is the minimal command to bring up Swift AIO, and it's dependencies:

::

  ansible-playbook \
    -i ansible/inventory/all-in-one \
    -e @/etc/kolla/globals.yml \
    -e @etc/kolla/passwords.yml \
    ansible/site.yml \
    --tags=rabbitmq,mariadb,keystone,swift

Validation
----------
A very basic smoke test:

::

  $ swift stat
                            Account: AUTH_4c19d363b9cf432a80e34f06b1fa5749
                       Containers: 1
                          Objects: 0
                            Bytes: 0
  Containers in policy "policy-0": 1
     Objects in policy "policy-0": 0
       Bytes in policy "policy-0": 0
      X-Account-Project-Domain-Id: default
                      X-Timestamp: 1440168098.28319
                       X-Trans-Id: txf5a62b7d7fc541f087703-0055d73be7
                     Content-Type: text/plain; charset=utf-8
                    Accept-Ranges: bytes

  $ swift upload mycontainer README.rst
  README.md

  $ swift list
  mycontainer

  $ swift download mycontainer README.md
  README.md [auth 0.248s, headers 0.939s, total 0.939s, 0.006 MB/s]
