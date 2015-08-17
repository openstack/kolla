# Developer Environment

If you are developing Kolla on an existing OpenStack cloud that supports
Heat, then follow the Heat template [README][].  Another option available
on systems with VirutalBox is the use of [Vagrant][].

The best experience is available with bare metal deployment by following
the instructions below to manually create your Kolla deployment.

[README]: https://github.com/stackforge/kolla/blob/master/devenv/README.md
[Vagrant]: https://github.com/stackforge/kolla/blob/master/docs/vagrant.md

## Installing Dependencies

NB: Kolla will not run on Fedora 22 or later.  Fedora 22 compresses kernel
modules with the .xz compressed format.  The guestfs system cannot read
these images because a dependent package supermin in CentOS needs to be
updated to add .xz compressed format support.

To install Kolla depenedencies use:

    git clone http://github.com/stackforge/kolla
    cd kolla
    sudo pip install -r requirements.txt

In order to run Kolla, it is mandatory to run a version of `docker` that is
1.7.0 or later.

For most systems you can install the latest stable version of Docker with the
following command:

    curl -sSL https://get.docker.io | bash

For Ubuntu based systems, do not use AUFS when starting Docker daemon unless
you are running the Utopic (3.19) kernel. AUFS requires CONFIG_AUFS_XATTR=y
set when building the kernel. On Ubuntu, versions prior to 3.19 did not set that
flag. If you are unable to upgrade your kernel, you should use a different
storage backend such as btrfs.

Next, install the OpenStack python clients if they are not installed:

    sudo pip install -U python-openstackclient

Finally stop libvirt on the host machine.  Only one copy of libvirt may be
running at a time.

    service libvirtd stop

The basic starting environment will be created using `ansible`.
This environment will start up the OpenStack services listed in the
inventory file.

## Starting Kolla

Configure Ansible by reading the Kolla Ansible configuration documentation
[DEPLOY][].

[DEPLOY]: https://github.com/stackforge/kolla/blob/master/docs/ansible-deployment.md

Next, run the start command:

    $ sudo ./tools/kolla-ansible deploy

A bare metal system takes three minutes to deploy AIO.  A virtual machine
takes five minutes to deploy AIO.  These are estimates; your hardware may
be faster or slower but should near these results.

## Debugging Kolla

You can determine a container's status by executing:

    $ sudo docker ps -a

If any of the containers exited you can check the logs by executing:

    $ sudo docker logs <container-name>
