Operating Kolla
===============

Upgrading
---------
TODO(all) fill this section out

Diagnostics
-----------
TODO(all) fill this section out

Failure Recovery
----------------
TODO(all) fill this section out

Reconfiguration of an existing environment
------------------------------------------
TODO(all) fill this section out

Tips and Tricks
---------------
Kolla ships with several utilities intended to facilitate ease of operation.

``tools/cleanup-containers`` can be used to remove deployed containers from
the system. This can be useful when you want to do a new clean deployment. It
will preserve the registry and the locally built images in the registry,
but will remove all running Kolla containers from the local Docker daemon.
It also removes the named volumes.

``tools/cleanup-host`` can be used to remove remnants of network changes
triggered on the Docker host when the neutron-agents containers are launched.
This can be useful when you want to do a new clean deployment, particularly
one changing the network topology.

``tools/cleanup-images`` can be used to remove all Docker images from the
local Docker cache. Note: this will remove the registry also.
