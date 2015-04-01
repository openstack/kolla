Koalla - Kolla with ansible!
============================

Koalla extends the Kolla project past [TripleO][] into its own bonified
deployment system using [Ansible][] and [docker-compose][].

[TripleO]: https://wiki.openstack.org/wiki/TripleO
[Ansible]: https://docs.ansible.com
[docker-compose]: http://docs.docker.com/compose


Getting Started
---------------

To run the ansible playbooks, you must specify an inventory file which tracks
all of the available nodes in your environment. With this inventory file
ansible will log into each node via ssh (configurable) and run tasks. Ansible
does not require password less logins via ssh, however it is highly recommended
to setup ssh-keys. More information on the ansible inventory file can be found
[here][].

[here]: https://docs.ansible.com/intro_inventory.html


Deploying
---------

For All-In-One deploys, you can run the following commands. These will setup all
of the containers on your localhost.

    cd ./kolla/ansible
    ansible-playbook -i inventory/all-in-one site.yml

To run the playbooks for only a particular service, you can us ansible tags.
Multiple tags may be specified, and order is still determined by the playbooks.

    cd ./kolla/ansible
    ansible-playbook -i inventory/all-in-one site.yml --tags message-broker
    ansible-playbook -i inventory/all-in-one site.yml --tags message-broker,database


Further Reading
---------------

Ansible playbook documentation can be found [here][].

[here]: http://docs.ansible.com/playbooks.html
