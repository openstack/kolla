Docker compose
==============

These scripts and docker compose files can be used to stand up a simple
installation of openstack.  Running the 'tools/genenv' script creates an
'openstack.env' suitable for running on a single host system as well as an
'openrc' to allow access to the installation.

Once you have run that you can either manually start the containers using the
'docker-compose' command or try the 'tools/start' script which tries to start them
all in a reasonable order, waiting at key points for services to become
available.  Once stood up you can issue the typical openstack commands to use
the installation:

```
# source openrc
# nova network-create vmnet --fixed-range-v4=10.0.0.0/24 --bridge=br100 --multi-host=T
# nova secgroup-add-rule default tcp 22 22 0.0.0.0/0
# nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
#
# nova keypair-add mykey > mykey.pem
# chmod 600 mykey.pem
# nova boot --flavor m1.medium --key_name mykey --image puffy_clouds instance_name
# ssh -i mykey.pem cirros@<ip>
```
