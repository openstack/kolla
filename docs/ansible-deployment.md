Kolla with Ansible!
============================

Kolla supports deploying Openstack using [Ansible][].

[Ansible]: https://docs.ansible.com


Getting Started
---------------

To run the Ansible playbooks, an inventory file which tracks all of the
available nodes in the environment must be speficied. With this inventory file
Ansible will log into each node via ssh (configurable) and run tasks. Ansible
does not require password-less logins via ssh, however it is highly recommended
to setup ssh-keys.

Two sample inventory files are provided, *all-in-one*, and *multinode*. The
"all-in-one" inventory defaults to use the Ansible "local" connection type,
which removes the need to setup ssh keys in order to get started quickly.

More information on the Ansible inventory file can be found [here][].

[here]: https://docs.ansible.com/intro_inventory.html

Deploying
---------

Add the etc/kolla directory to /etc/kolla on the deployment host. Inside of
this directory are two files and a minimum number of parameters which are
listed below.

All variables for the environment can be specified in the files:
"/etc/kolla/globals.yml" and "/etc/kolla/passwords.yml"

The kolla_*_address variables can both be the same. Please specify an unused IP
address in your network to act as a VIP for kolla_internal_address. The VIP will
be used with keepalived and added to your "api_interface" as specified in the
globals.yml

    kolla_external_address: "openstack.example.com"
    kolla_internal_address: "10.10.10.254"

The "network_interface" variable is the interface that we bind all our services
to. For example, when starting up Mariadb it will bind to the IP on the
interface list in the "network_interface" variable.

    network_interface: "eth0"

The "neutron_external_interface" variable is the interface that will be used for
your external bridge in Neutron. Without this bridge your instance traffic will
be unable to access the rest of the Internet. In the case of a single interface
on a machine, you may use a veth pair where one end of the veth pair is listed
here and the other end is in a bridge on your system.

    neutron_external_interface: "eth1"

The docker_pull_policy specifies whether Docker should always pull images from
the repository it is configured for, or only in the case where the image isn't
present locally. If you are building your own images locally without pushing
them to the Docker Registry, or a local registry, you must set this value to
"missing" or when you run the playbooks docker will attempt to fetch the latest
image upstream.

    docker_pull_policy: "always"

You must also have the following dependencies installed on each of the target nodes:

* MySQL-python
* docker-py (>1.2.0)
* shade

On RPM based distros these may be installed as follows:

    sudo yum install -y \
        gcc \
        libffi-devel \
        libxml2-devel \
        libxslt-devel \
        MySQL-python \
        openssl \
        openssl-devel \
        python-devel
    sudo pip install docker-py shade

This setup will be automated as part of a future release.

For All-In-One deploys, the following commands can be run. These will setup all
of the containers on the localhost. These commands will be wrapped in the
kolla-script in the future.

    cd ./kolla/ansible
    ansible-playbook -i inventory/all-in-one -e @/etc/kolla/defaults.yml -e @/etc/kolla/globals.yml -e @/etc/kolla/passwords.yml site.yml

To run the playbooks for only a particular service, Ansible tags can be used.
Multiple tags may be specified, and order is still determined by the playbooks.

    cd ./kolla/ansible
    ansible-playbook -i inventory/all-in-one -e @/etc/kolla/defaults.yml -e @/etc/kolla/globals.yml -e @/etc/kolla/passwords.yml site.yml --tags rabbitmq
    ansible-playbook -i inventory/all-in-one -e @/etc/kolla/defaults.yml -e @/etc/kolla/globals.yml -e @/etc/kolla/passwords.yml site.yml --tags rabbitmq,mariadb

Finally, you can view ./kolla/tools/openrc-example for an example of an openrc
you can use with your environment. If you wish you may also run the following
command to initiate your environment with an glance image and neutron networks.

    cd ./kolla/tools
    ./init-runonce

Further Reading
---------------

Ansible playbook documentation can be found [here][].

[here]: http://docs.ansible.com/playbooks.html
