Docker compose
==============

These scripts and docker compose files can be used to stand up a simple
installation of openstack.  Running the 'tools/genenv' script creates an
'openstack.env' suitable for running on a single host system as well as an
'openrc' to allow access to the installation.

Once you have run that you can either manually start the containers using the
'docker-compose' command or try the 'tools/kolla-compose start' script which tries to
start them all in a reasonable order, waiting at key points for services to
become available.  Once stood up you can issue the typical openstack commands
to use the installation.  If using nova networking use:

```
# source openrc
# tools/init-runonce
# nova boot --flavor m1.medium --key_name mykey --image puffy_clouds instance_name
# ssh cirros@<ip>
```

Else if using neutron networking use:

```
# source openrc
# tools/init-runonce
# nova boot --flavor m1.medium --key_name mykey --image puffy_clouds instance_name --nic net-id:<net id>
# ssh cirros@<ip>
```
