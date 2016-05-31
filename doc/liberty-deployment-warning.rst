.. _liberty-deployment-warning:

================================
Liberty 1.0.0 Deployment Warning
================================

Warning Overview
================
Please use Liberty 1.1.0 tag or later when using Kolla. No data loss
occurs with this version. ``stable/liberty`` is also fully functional and
suffers no data loss.

Data loss with 1.0.0
====================
The Kolla community discovered in the of middle Mitaka development that it
was possible for data loss to occur if the data container is rebuilt. In
this scenario, Docker pulls a new container, and the new container doesn't
contain the data from the old container. Kolla ``stable/liberty`` and Kolla
1.0.0 are not to be used at this time, as they result in **critical data loss
problems**.

Resolution
==========
To rectify this problem, the OpenStack release and infrastructure teams
in coordination with the Kolla team executed the following actions:

* Deleted the ``stable/liberty`` branch (where 1.0.0 was tagged from)
* Created a tag liberty-early-demise at the end of the broken ``stable/liberty``
  branch development.
* Created a new ``stable/liberty`` branch based upon ``stable/mitaka``.
* Corrected ``stable/liberty`` to deploy Liberty.
* Released Kolla 1.1.0 from the newly created ``stable/liberty`` branch.

End Result
==========
A fully functional Liberty OpenStack deployment based upon the two years of
testing that went into the development that went into ``stable/mitaka``.

The docker-engine 1.10.0 or later is required.
