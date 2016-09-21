.. _external-ceph-guide:

=============
External Ceph
=============

Sometimes it is necessary to connect OpenStack services to an existing Ceph
cluster instead of deploying it with Kolla. This can be achieved with only a
few configuration steps in Kolla.

Requirements
============

* An existing installation of Ceph
* Existing Ceph storage pools
* Existing credentials in Ceph for OpenStack services to connect to Ceph
  (Glance, Cinder, Nova)

Enabling External Ceph
======================

Using external Ceph with Kolla means not to deploy Ceph via Kolla. Therefore,
disable Ceph deployment in ``/etc/kolla/global.yml``

::

  enable_ceph: "no"

There are flags indicating individual services to use ceph or not which default
to the value of ``enable_ceph``. Those flags now need to be activated in order
to activate external Ceph integration. This can be done individually per
service in ``/etc/kolla/global.yml``:

::

  glance_backend_ceph: "yes"
  cinder_backend_ceph: "yes"

The combination of ``enable_ceph: "no"`` and ``<service>_backend_ceph: "yes"``
triggers the activation of external ceph mechanism in Kolla.

Configuring External Ceph
=========================

Glance
------

Configuring Glance for Ceph includes three steps:

1) Configure RBD backend in glance-api.conf
2) Create Ceph configuration file in /etc/ceph/ceph.conf
3) Create Ceph keyring file in /etc/ceph/ceph.client.<username>.keyring

Step 1 is done by using Kolla's INI merge mechanism: Create a file in
``/etc/kolla/config/glance/glance-api.conf`` with the following contents:

::

  [DEFAULT]
  show_image_direct_url = True

  [glance_store]
  stores = rbd
  default_store = rbd
  rbd_store_pool = images
  rbd_store_user = glance
  rbd_store_ceph_conf = /etc/ceph/ceph.conf

  [image_format]
  container_formats = bare
  disk_formats = raw

Now put ceph.conf and the keyring file (name depends on the username created in
Ceph) into the same directory, for example:

/etc/kolla/config/glance/ceph.conf

::

  [global]
  fsid = 1d89fec3-325a-4963-a950-c4afedd37fe3
  mon_initial_members = ceph-0
  mon_host = 192.168.0.56
  auth_cluster_required = cephx
  auth_service_required = cephx
  auth_client_required = cephx

/etc/kolla/config/glance/ceph.client.glance.keyring

::

  [client.glance]
  key = AQAg5YRXS0qxLRAAXe6a4R1a15AoRx7ft80DhA==

Kolla will pick up all files named ceph.* in this directory an copy them to the
/etc/ceph/ directory of the container.

Cinder
------

Configuring external Ceph for Cinder works very similar to
Glance. The required Cinder configuration goes into
/etc/kolla/config/cinder/cinder-volume.conf:

::

  [DEFAULT]
  enabled_backends=rbd-1

  [rbd-1]
  rbd_ceph_conf=/etc/ceph/ceph.conf
  rbd_user=cinder
  backend_host=rbd:volumes
  rbd_pool=volumes
  volume_backend_name=rbd-1
  volume_driver=cinder.volume.drivers.rbd.RBDDriver

Next, place the ceph.conf file into
/etc/kolla/config/cinder/ceph.conf:

::

  [global]
  fsid = 1d89fec3-325a-4963-a950-c4afedd37fe3
  mon_initial_members = ceph-0
  mon_host = 192.168.0.56
  auth_cluster_required = cephx
  auth_service_required = cephx
  auth_client_required = cephx

Separate configuration options can be configured for
cinder-volume and cinder-backup by adding ceph.conf files to
/etc/kolla/config/cinder/cinder-volume and
/etc/kolla/config/cinder/cinder-backup respectively. They
will be merged with /etc/kolla/config/cinder/ceph.conf.

Ceph keyrings are deployed per service and placed into
cinder-volume and cinder-backup directories:

::

  root@deploy:/etc/kolla/config# cat
  cinder/cinder-backup/ceph.client.cinder.keyring
  [client.cinder]
          key = AQAg5YRXpChaGRAAlTSCleesthCRmCYrfQVX1w==
  root@deploy:/etc/kolla/config# cat
  cinder/cinder-volume/ceph.client.cinder.keyring
  [client.cinder]
          key = AQAg5YRXpChaGRAAlTSCleesthCRmCYrfQVX1w==

It is important that the files are named ceph.client*.

Nova
------

In ``/etc/kolla/global.yml`` set

::

  nova_backend_ceph: "yes"

Put ceph.conf and keyring file into ``/etc/kolla/config/nova``:

::

  $ ls /etc/kolla/config/nova
  ceph.client.nova.keyring ceph.conf

Configure nova-compute to use Ceph as the ephemeral backend by creating
``/etc/kolla/config/nova/nova-compute.conf`` and adding the following
contents:

::

  [libvirt]
  images_rbd_pool=vms
  images_type=rbd
  images_rbd_ceph_conf=/etc/ceph/ceph.conf
  rbd_user=nova

.. note:: ``rbd_user`` might vary depending on your environment.
