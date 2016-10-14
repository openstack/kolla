A Kolla Demo using Heat
=======================

By default, the launch script will spawn 3 Nova instances on a Neutron
network created from the tools/init-runonce script. Edit the VM\_COUNT
parameter in the launch script if you would like to spawn a different
amount of Nova instances. Edit the IMAGE\_FLAVOR if you would like to
launch images using a flavor other than m1.tiny.

Then run the script:

::

    $ ./launch

