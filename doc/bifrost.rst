=============
Bifrost Guide
=============


Prep host
=========

Clone kolla
-----------

::

    git clone https://github.com/openstack/kolla
    cd kolla

set up kolla dependencies :doc:`quickstart`

Fix hosts file
--------------

Docker bind mounts ``/etc/hosts`` into the container from a volume
This prevents atomic renames which will prevent ansible from fixing
the ``/etc/hosts`` file automatically.

To enable bifrost to be bootstrapped correctly add the deployment
hosts hostname to 127.0.0.1 line for example:

::

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


Enable source build type
========================

Via config file
---------------

::

    tox -e genconfig

Modify ``kolla-build.conf`` as follows.
Set ``install_type`` to ``source``

::

    install_type = source

Command line
------------

Alternatively if you do not wish to use the ``kolla-build.conf``
you can enable a source build by appending ``-t source`` to
your ``kolla-build`` or ``tools/build.py`` command.

Build container
===============

Development
-----------

::

    tools/build.py bifrost-deploy

Production
----------

::

    kolla-build bifrost-deploy

Prepare bifrost configs
=======================

Create servers.yml
------------------

The ``servers.yml`` will describing your physical nodes and list IPMI credentials.
See bifrost dynamic inventory examples for more details.

For example ``/etc/kolla/config/bifrost/servers.yml``

.. code-block:: yaml

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

Create bifrost.yml
------------------
By default kolla mostly use bifrosts default playbook values.
Parameters passed to the bifrost install playbook can be overridden by
creating a ``bifrost.yml`` file in the kolla custom config directory or in a
bifrost sub directory.
For example ``/etc/kolla/config/bifrost/bifrost.yml``

::

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
by creating a ``dib.yml`` file in the kolla custom config directory or in a
bifrost sub directory.
For example ``/etc/kolla/config/bifrost/dib.yml``

::

    dib_os_element: ubuntu

Deploy Bifrost
=========================

Ansible
-------

Development
___________

::

    tools/kolla-ansible deploy-bifrost

Production
__________

::

    kolla-ansible deploy-bifrost

Manual
------

Start Bifrost Container
_______________________
::

    docker run -it --net=host -v /dev:/dev -d --privileged --name bifrost_deploy kolla/ubuntu-source-bifrost-deploy:3.0.1

Copy configs
____________

.. code-block:: console

    docker exec -it bifrost_deploy mkdir /etc/bifrost
    docker cp /etc/kolla/config/bifrost/servers.yml bifrost_deploy:/etc/bifrost/servers.yml
    docker cp /etc/kolla/config/bifrost/bifrost.yml bifrost_deploy:/etc/bifrost/bifrost.yml
    docker cp /etc/kolla/config/bifrost/dib.yml bifrost_deploy:/etc/bifrost/dib.yml

Bootstrap bifrost
_________________

::

    docker exec -it bifrost_deploy bash

Generate ssh key
~~~~~~~~~~~~~~~~

::

    ssh-keygen

Source env variables
~~~~~~~~~~~~~~~~~~~~

::

    cd /bifrost
    . env-vars
    . /opt/stack/ansible/hacking/env-setup
    cd playbooks/


Bootstrap and start services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: console

    ansible-playbook -vvvv -i /bifrost/playbooks/inventory/localhost /bifrost/playbooks/install.yaml -e @/etc/bifrost/bifrost.yml

Check ironic is running
=======================

.. code-block:: console

    docker exec -it bifrost_deploy bash
    cd /bifrost
    . env-vars

Running "ironic node-list" should return with no nodes, for example

.. code-block:: console

    (bifrost-deploy)[root@bifrost bifrost]# ironic node-list
    +------+------+---------------+-------------+--------------------+-------------+
    | UUID | Name | Instance UUID | Power State | Provisioning State | Maintenance |
    +------+------+---------------+-------------+--------------------+-------------+
    +------+------+---------------+-------------+--------------------+-------------+


Enroll and Deploy Physical Nodes
================================

Ansible
-------

Development
___________

::

    tools/kolla-ansible deploy-servers

Production
__________

::

    kolla-ansible deploy-servers


Manual
------
.. code-block:: console

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

At this point ironic should clean down your nodes and install the default
os image.

Advanced configuration
======================

Bring your own image
--------------------
TODO

Bring your own ssh key
----------------------
To use your own ssh key after you have generated the ``passwords.yml`` file
update the private and public keys under bifrost_ssh_key.

Known issues
============

SSH daemon not running
----------------------
By default sshd is installed in the image but may not be enabled.
If you encounter this issue you will have to access the server physically in
recovery mode to enable the ssh service. If your hardware supports it, this
can be done remotely with ipmitool and serial over lan. For example

.. code-block:: console

    ipmitool -I lanplus -H 192.168.1.30 -U admin -P root sol activate


References
==========

Docs: http://docs.openstack.org/developer/bifrost/

Troubleshooting: http://docs.openstack.org/developer/bifrost/troubleshooting.html

Code: https://github.com/openstack/bifrost

