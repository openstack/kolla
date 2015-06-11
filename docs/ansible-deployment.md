Koalla - Kolla with Ansible!
============================

Koalla extends the Kolla project past [TripleO][] into its own bonified
deployment system using [Ansible][] and [docker-compose][].

[TripleO]: https://wiki.openstack.org/wiki/TripleO
[Ansible]: https://docs.ansible.com
[docker-compose]: http://docs.docker.com/compose


Getting Started
---------------

To run the Ansible playbooks, you must specify an inventory file which tracks
all of the available nodes in your environment. With this inventory file
Ansible will log into each node via ssh (configurable) and run tasks. Ansible
does not require password less logins via ssh, however it is highly recommended
to setup ssh-keys.

Two sample inventory files are provided, *all-in-one*, and *multinode*. The
"all-in-one" inventory defaults to use the Ansible "local" connection type,
which removes the need to setup ssh keys in order to get started quickly.

More information on the Ansible inventory file can be found [here][].

[here]: https://docs.ansible.com/intro_inventory.html


Deploying
---------

You can adjust variables for your environment in the file:
"./kolla/ansible/group_vars/all.yml"
Ensure that the *koalla_directory* variable matches where you have Kolla cloned
on the target machine(s).

For All-In-One deploys, you can run the following commands. These will setup all
of the containers on your localhost.

    cd ./kolla/ansible
    ansible-playbook -i inventory/all-in-one site.yml

To run the playbooks for only a particular service, you can use Ansible tags.
Multiple tags may be specified, and order is still determined by the playbooks.

    cd ./kolla/ansible
    ansible-playbook -i inventory/all-in-one site.yml --tags message-broker
    ansible-playbook -i inventory/all-in-one site.yml --tags message-broker,database


Further Reading
---------------

Ansible playbook documentation can be found [here][].

[here]: http://docs.ansible.com/playbooks.html
