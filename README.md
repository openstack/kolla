Kolla
=====

The Kolla project is part of the OpenStack TripleO effort, focused on
deploying OpenStack environments using [Kubernetes][] and [Docker][]
containers.

[kubernetes]: https://github.com/GoogleCloudPlatform/kubernetes
[docker]: http://docker.com/

Getting Started
===============

Kubernetes deployment on bare metal is a complex topic which is beyond the
scope of this project at this time.  The developers still require a test
environment.  As a result, one of the developers has created a Heat based
deployment tool that can be
found [here](https://github.com/larsks/heat-kubernetes).


Build Docker Images 
-------------------

Within the docker directory is a tool called build.  This tool will build
all of the docker images that have been implemented.  Each OpenStack service is
implemented as a separate container that can later be registered with
Kubernetes.

** [sdake@bigiron docker]$ sudo ./build **

A 20-30 minute build process will begin where containers will be built for
each OpenStack service.  Once finished the docker images can be examined with
the docker CLI.

** [sdake@bigiron docker]$ sudo docker images **

A list of the built docker images will be shown.

Note at this time the images do not yet work correctly or operate on their
defined environment variables.  They are essentially placeholders.


Use Kubernetes to Deploy OpenStack
----------------------------------

This has not been implemented.


Directories
===========

* docker - contains artifacts for use with docker build to build appropriate images
