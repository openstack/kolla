=============
Bifrost Guide
=============


Prep host
=========

clone kolla
-----------
git clone https://github.com/openstack/kolla

cd kolla

set up kolla dependcies `doc`:quickstart.rst

fix hosts file
--------------
Docker bind mounts ``/etc/hosts`` into the container from a volume.
This prevents atomic renames which will prevent ansible from fixing
the ``/etc/hosts`` file automatically.

to enable bifrost to be bootstrapped correctly
add the deployment hosts hostname to 127.0.0.1 line
e.g.

ubuntu@bifrost:/repo/kolla$ cat /etc/hosts
127.0.0.1 bifrost localhost

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
192.168.100.15 bifrost


enable source build type
========================

via config file
---------------

tox -e genconfig

modify kolla-build.conf as follows.

set install_type to source

command line
------------
alternitivly if you do not wish to use the kolla-build.conf
you can enable a source build by appending ``-t source`` to
your kolla-build or tools/build.py command.

build container
===============

Development
-----------
tools/build.py bifrost-deploy

Production
----------
kolla-build bifrost-deploy


Prepare bifrost configs
=======================

create servers.yml
------------------

the servers.yml will discribing your physical nodes and list ipmi credentials.
see bifrost dynamic inventory examples for mor details.

e.g. /etc/kolla/config/bifrost/servers.yml

---
cloud1:
    uuid: "31303735-3934-4247-3830-333132535336"
    driver_info:
      power:
        ipmi_username: "admin"
        ipmi_address: "192.168.1.30"
        ipmi_password: "root"
    nics:
      -
        mac: "1c:c1:de:1c:aa:53"
      -
        mac: "1c:c1:de:1c:aa:52"
    driver: "agent_ipmitool"
    ipv4_address: "192.168.1.10"
    properties:
      cpu_arch: "x86_64"
      ram: "24576"
      disk_size: "120"
      cpus: "16"
    name: "cloud1"

adjust as appropriate for your deployment

create bifrost.yml
------------------
By default kolla mostly use bifrosts default playbook values.
Parameters passed to the bifrost install playbook can be overridden by
creating a bifrost.yml file in the kolla custom config director or in a
bifrost sub directory.
e.g. /etc/kolla/config/bifrost/bifrost.yml

    mysql_service_name: mysql
    ansible_python_interpreter: /var/lib/kolla/venv/bin/python
    network_interface: < add you network interface here >
    # uncomment below if needed
    # dhcp_pool_start: 192.168.2.200
    # dhcp_pool_end: 192.168.2.250
    # dhcp_lease_time: 12h
    # dhcp_static_mask: 255.255.255.0

Create Disk Image Builder Config
--------------------------------
By default kolla mostly use bifrosts default playbook values when
building the baremetal os image. The baremetal os image can be customised
by creating a dib.yml file in the kolla custom config director or in a
bifrost sub directory.
e.g. /etc/kolla/config/bifrost/dib.yml

dib_os_element: ubuntu


Deploy Bifrost
=========================

ansible
-------

Development
___________
tools/kolla-ansible deploy-bifrost

Production
__________
kolla-ansible deploy-bifrost

manual
------

Start Bifrost Container
_______________________
docker run -it --net=host -v /dev:/dev -d --privileged --name bifrost_deploy 192.168.1.51:5000/kollaglue/ubuntu-source-bifrost-deploy:3.0.0

copy configs
____________

docker exec -it bifrost_deploy mkdir /etc/bifrost
docker cp /etc/kolla/config/bifrost/servers.yml bifrost_deploy:/etc/bifrost/servers.yml
docker cp /etc/kolla/config/bifrost/bifrost.yml bifrost_deploy:/etc/bifrost/bifrost.yml
docker cp /etc/kolla/config/bifrost/dib.yml bifrost_deploy:/etc/bifrost/dib.yml

bootstrap bifrost
_________________

docker exec -it bifrost_deploy bash

generate ssh key
~~~~~~~~~~~~~~~~

ssh-keygen

source env variables
~~~~~~~~~~~~~~~~~~~~
cd /bifrost
. env-vars
. /opt/stack/ansible/hacking/env-setup
cd playbooks/


bootstrap and start services
~~~~~~~~~~~~~~~~~~~~~~~~~~~
ansible-playbook -vvvv -i /bifrost/playbooks/inventory/localhost /bifrost/playbooks/install.yaml -e @/etc/bifrost/bifrost.yml

Check ironic is running
=======================


docker exec -it bifrost_deploy bash
cd /bifrost
. env-vars
running "ironic node-list" should return with no nodes.
e.g.

(bifrost-deploy)[root@bifrost bifrost]# ironic node-list
+------+------+---------------+-------------+--------------------+-------------+
| UUID | Name | Instance UUID | Power State | Provisioning State | Maintenance |
+------+------+---------------+-------------+--------------------+-------------+
+------+------+---------------+-------------+--------------------+-------------+


Enroll and Deploy Physical Nodes
================================

ansible
-------

Development
___________
tools/kolla-ansible deploy-servers

Production
__________
kolla-ansible deploy-servers


manual
------
docker exec -it bifrost_deploy bash
cd /bifrost
. env-vars
export BIFROST_INVENTORY_SOURCE=/etc/bifrost/servers.yml
ansible-playbook -vvvv -i inventory/bifrost_inventory.py enroll-dynamic.yaml -e "ansible_python_interpreter=/var/lib/kolla/venv/bin/python" -e network_interface=<provisioning interface>

docker exec -it bifrost_deploy bash
cd /bifrost
. env-vars
export BIFROST_INVENTORY_SOURCE=/etc/bifrost/servers.yml
ansible-playbook -vvvv -i inventory/bifrost_inventory.py deploy-dynamic.yaml -e "ansible_python_interpreter=/var/lib/kolla/venv/bin/python" -e network_interface=<prvisioning interface> -e @/etc/bifrost/dib.yml

At this point ironic should clean down your nodes and install the default os image.

Advanced configuration
======================

Bring your own image
--------------------
TODO

Bring your own ssh key
----------------------
To use your own ssh key after you have generated the passwords.yml file
update the private and public keys under bifrost_ssh_key.

Known issues
============

SSH deamon not running
----------------------
By default sshd is installed in the image but may not be enabled.
If you encounter this issue you will have to acess the server phyically in recovery mode to enable the ssh service.
if your hardware supports it, this can be done remotely with ipmitool and serial over lan.
e.g.
ipmitool -I lanplus -H 192.168.1.30 -U admin -P root sol activate


References
==========

Bifrost
-------
docs
____
http://docs.openstack.org/developer/bifrost/

troubleshooting
_______________
http://docs.openstack.org/developer/bifrost/troubleshooting.html

code
____
https://github.com/openstack/bifrost


