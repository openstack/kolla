# Image building

The `tools/build-docker-image` script in this repository is
responsible for building docker images.  It is symlinked as `./build`
inside each Docker image directory.

When creating new image directories, you can run the
`tools/update-build-links` scripts to install the `build` symlink
(this script will install the symlink anywhere it find a file named
`Dockerfile`).

## Workflow

In general, you will build images like this:

    $ cd docker/keystone
    $ ./build

By default, the above command would build
`kollaglue/fedora-rdo-keystone:CID`, where `CID` is the current short
commit ID.  That is, given:

    $ git rev-parse HEAD
    76a16029006a2f5d3b79f1198d81acb6653110e9

The above command would generate
`kollaglue/fedora-rdo-keystone:76a1602`.  This tagging is meant to
prevent developers from stepping on each other or on release images
during the development process.

To push the image after building, add `--push`:

    $ ./build --push

To use these images, you must specify the tag in your `docker run`
commands:

    $ docker run kollaglue/fedora-rdo-keystone:76a1602

Or in your kubernetes configurations:

    "containers": [{
      "name": "keystone",
      "image": "kollaglue/fedora-rdo-keystone:76a1602",
      "ports": [
        {"containerPort": 5000},
        {"containerPort": 35357}
      ],
      "env": [
        {"name": "DB_ROOT_PASSWORD", "value": "password"},
        {"name": "KEYSTONE_ADMIN_TOKEN", "value": "ADMINTOKEN"}
      ]
    }]

## Building releases

To build into the `latest` tag, add `--release`:

    $ ./build --release

Or to build and push:

    $ ./build --push --release

## Configuration

The `build-docker-image` script will look for a file named `.buildconf`
in your current directory and in the top level of the repository.  You
can use this to set defaults, such as:

    NAMESPACE=larsks

This setting would cause all images to be tagged into the `larsks/`
namespace.

