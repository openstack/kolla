..
      Copyright 2014-2015 OpenStack Foundation
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

=================================
Welcome to Kolla's documentation!
=================================

Kolla's Mission
===============

Kolla provides Docker containers and Ansible playbooks to meet Kolla's mission.
Kolla's mission is to provide production-ready containers and deployment tools
for operating OpenStack clouds.

Kolla is highly opinionated out of the box, but allows for complete
customization. This permits operators with minimal experience to deploy
OpenStack quickly and as experience grows modify the OpenStack configuration to
suit the operator's exact requirements.

Site Notes
==========

This documentation is continually updated and may not represent the state of
the project at any specific prior release. To access documentation for a
previous release of kolla, append the OpenStack release name to the URL, for
example:

    http://docs.openstack.org/developer/kolla/mitaka/


Kolla Overview
==============

.. toctree::
   :maxdepth: 1

   deployment-philosophy
   production-architecture-guide
   quickstart
   multinode
   image-building
   advanced-configuration
   operating-kolla
   security

Kolla Services
==============

.. toctree::
   :maxdepth: 1

   ceph-guide
   external-ceph-guide
   cinder-guide
   ironic-guide
   manila-guide
   swift-guide
   kibana-guide
   bifrost
   networking-guide
   kuryr-guide

Developer Docs
==============

.. toctree::
   :maxdepth: 1

   CONTRIBUTING
   vagrant-dev-env
   running-tests
   bug-triage
