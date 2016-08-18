.. _deployment-philosophy:

=============================
Kolla's Deployment Philosophy
=============================

Overview
========

Kolla has an objective to replace the inflexible, painful, resource-intensive
deployment process of OpenStack with a flexible, painless, inexpensive
deployment process. Often to deploy OpenStack at the 100+ node scale small
businesses may require means building a team of OpenStack professionals to
maintain and manage the OpenStack deployment. Finding people experienced in
OpenStack deployment is very difficult and expensive, resulting in a big
barrier for OpenStack adoption. Kolla seeks to remedy this set of problems by
simplifying the deployment process but enabling flexible deployment models.

Kolla is a highly opinionated deployment tool out of the box. This permits
Kolla to be deployable with the simple configuration of three key/value pairs.
As an operator's experience with OpenStack grows and the desire to customize
OpenStack services increases, Kolla offers full capability to override every
OpenStack service configuration option in the deployment.

Templating and Customization Philosophy
=======================================

To read up on the Kolla communities template philosphy go to the
:doc:`templating` doc.

Architecture
============

#TODO: Link an image showing the architecture


.. toctree::
   :hidden:

   templating
