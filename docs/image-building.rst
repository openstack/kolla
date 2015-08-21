Image building
==============

The ``tools/build-docker-image`` script in this repository is
responsible for building docker images. It is symlinked as ``./build``
inside each Docker image directory.

When creating new image directories, you can run the
``tools/update-build-links`` scripts to install the ``build`` symlink
(this script will install the symlink anywhere it find a file named
``Dockerfile``).

Workflow
--------

In general, you will build images like this:

::

    $ cd docker/keystone
    $ ./build

By default, the above command would build
``kollaglue/centos-rdo-keystone:CID``, where ``CID`` is the current
short commit ID. That is, given:

::

    $ git rev-parse HEAD
    76a16029006a2f5d3b79f1198d81acb6653110e9

The above command would generate
``kollaglue/centos-rdo-keystone:76a1602``. This tagging is meant to
prevent developers from stepping on each other or on release images
during the development process.

To push the image after building, add ``--push``:

::

    $ ./build --push

To use these images, you must specify the tag in your ``docker run``
commands:

::

    $ docker run kollaglue/centos-rdo-keystone:76a1602

Building releases
-----------------

To build into the ``latest`` tag, add ``--release``:

::

    $ ./build --release

Or to build and push:

::

    $ ./build --push --release

Build all images at once
------------------------

The ``build-all-docker-images`` script in the tools directory is a
wrapper for the ``build-docker-image`` that builds all images, as the
name suggests, in the correct order. It responds to the same options as
``build-docker-image`` with the additional ``--from`` and ``--to``
options that allows building only images that have changed between the
specified git revisions.

For example, to build all images contained in docker directory and push
new release:

::

    $ tools/build-all-docker-images --release --push

To build only images modified in test-branch along with their children:

::

    $ tools/build-all-docker-images --from master --to test-branch

Configuration
-------------

The ``build-docker-image`` script will look for a file named
``.buildconf`` in the image directory and in the top level of the
repository. You can use this to set defaults, such as:

::

    NAMESPACE=larsks
    PREFIX=fedora-rdo-

This setting would cause images to be tagged into the ``larsks/``
namespace and use Fedora as base image instead of the default CentOS.
