Liberty 1.0.0 Deployment Warning
================================

Warning Overview
----------------
The Kolla community discovered in the of middle Mitaka development that it
was possible for data loss to occur if the data container is rebuilt.  In
this scenario, Docker pulls a new container, and the new container doesn't
contain the data from the old container.  Kolla stable/liberty and Kolla
1.0.0 are not to be used at this time, as they result in *critical data loss
problems*.

Resolution
----------
To rectify this problem, we plan to have a release of 1.1.0-rc1 on
April 1st, 2016.  We plan our final releae of 1.1.0 on April 15th, 2016.  The
work going into this version will be:

* Move forward to Docker 1.10.z as a minimum dependency.
* Move to named volumes to remove data loss scenario.
* Backport upgrade playbooks from Mitaka so Operators may effectively manage
  OSSA and CVE advisories in their OpenStack cloud without being forced to
  migrate to Mitaka.
* Backport thin-containers for Neutron agents.
* Backport Kolla's docker integration module to remove the hard pin on
  Docker 1.8.2.
* The Kolla community expects the docker containers themselves to be
  minimally modified.
