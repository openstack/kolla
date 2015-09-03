Image building
==============

The ``tools/build.py`` script in this repository is
responsible for building docker images. 

Guide
-----

In general, you will build images like this:

::

    $ tools/build.py

By default, the above command would build all images based on centos image.

If you want to change the base distro image, add ``-b``:

::

    $ tools/build.py -b ubuntu

There are following distros available for building images:

- fedora
- centos
- oraclelinux
- ubuntu

To push the image after building, add ``--push``:

::

    $ tools/build.py --push


If you want to build only keystone image, use the following command:

::

    $ tools/build.py keystone


If you want to build multiple images e.g. keystone and nova, use the following command:

::

    $ tools/build.py keystone nova


``tools/build.py`` use ``kollaglue`` as default namespace. If you
want to push images to your dockerhub, change the namespace like:

::

   $ tools/build.py -n yourusername --push


Build Openstack from Source
---------------------------

When building images, there are two methods of the Openstack install.
One is ``binary``. Another is ``source``.
The ``binary`` means that Openstack will be installed from apt/yum.
And the ``source`` means that Openstack will be installed from source code.
The default method of the Openstack install is ``binary``. 
You can change it to ``source`` using the following command:

::

    tools/build.py -t source

The locations of Opentack source code are written in ``build.ini``.
Now the source type support ``url`` and ``git``. The ``build.ini`` looks like:

::

    [glance-base]
    type = url
    location = http://tarballs.openstack.org/glance/glance-master.tar.gz

    [keystone]
    type = git
    location = https://github.com/openstack/keystone
    reference = stable/kilo
