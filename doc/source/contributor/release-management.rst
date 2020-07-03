==================
Release Management
==================

This guide is intended to complement the `OpenStack releases site
<https://releases.openstack.org/>`__, and the project team guide's section on
`release management
<https://docs.openstack.org/project-team-guide/release-management.html>`__.

Team members make themselves familiar with the release schedule for the current
release, for example https://releases.openstack.org/train/schedule.html.

Release Model
=============

As a deployment project, Kolla's release model differs from many other
OpenStack projects. Kolla follows the `cycle-trailing
<https://docs.openstack.org/project-team-guide/release-management.html#trailing-the-common-cycle>`__
release model, to allow time after the OpenStack coordinated release to wait
for distribution packages and support new features. This gives us three months
after the final release to prepare our final releases. Users are typically keen
to try out the new release, so we should aim to release as early as possible
while ensuring we have confidence in the release.

Release Schedule
================

While we don't wish to repeat the OpenStack release documentation, we will
point out the high level schedule, and draw attention to areas where our
process is different.

Launchpad Admin
---------------

We track series (e.g. Stein) and milestones (e.g. stein-1) on Launchpad, and
target bugs and blueprints to these. Populating these in advance is necessary.
This needs to be done for each of the following projects:

* https://launchpad.net/kolla

* https://launchpad.net/kolla-ansible

At the beginning of a cycle, ensure a named series exists for the cycle in each
project. If not, create one via the project landing page (e.g.
https://launchpad.net/kolla) - in the "Series and milestones" section click in
"Register a series". Once the series has been created, create the necessary
milestones, including the final release. Series can be marked as "Active
Development" or "Current Stable Release" as necessary.

Milestones
----------

At each of the various release milestones, pay attention to what other projects
are doing.

Feature Freeze
--------------

As with projects following the common release model, Kolla uses a feature
freeze period to allow the code to stabilise prior to release. There is no
official feature freeze date for the cycle-trailing model, but we typically
freeze around **three weeks** after the common feature freeze. During this
time, no features should be merged to the master branch.

Before RC1
----------

Prior to creating a release candidate:

* test the code and fix (at a minimum) all critical bugs

* the release notes for each project should be tidied up

  * this command is useful to list release notes added this cycle:

    * ``git diff --name-only origin/stable/<previous release> --
      releasenotes/``

  * example (kolla): https://review.opendev.org/648677/

  * example (kolla-ansible): https://review.opendev.org/648685/

* mark bugs on Launchpad with the correct milestone

  * this command is useful to check for commits that fixed bugs:

    * ``git log origin/stable/<previous release>..origin/master | grep -i
      Closes-Bug``

* update dependencies for source images on master to use release candidates:

  * ``./tools/version-check.py --openstack-release $SERIES``

  * this will only work when release candidates have been created for the
    dependent projects

  * add ``--include-independent`` to update projects with an independent
    release cycle

  * example (kolla): https://review.opendev.org/647819

* update ``OPENSTACK_RELEASE`` variable in ``kolla/common/config.py``

  * example (kolla): https://review.opendev.org/689729

* add `cycle highlights
  <https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights>`__
  when requested by the release team

  * example (all): https://review.opendev.org/644506/

RC1
---

RC1 is the first release candidate, and also marks the point at which the
stable branch is cut.

* create RC1 by submitting patches to the releases repository

  * example (kolla): https://review.opendev.org/650236

  * example (kolla-ansible): https://review.opendev.org/650237

* create stable branches by submitting patches to the releases repository

  * example (kolla): https://review.opendev.org/650411

  * example (kolla-ansible): https://review.opendev.org/650412

After RC1
---------

* approve bot-proposed patches to master and the new stable branch

* revert the patch to use release candidates of dependencies on the master
  branch

  * example (kolla): https://review.opendev.org/650419

* revert the patch to switch OPENSTACK_RELEASE in kolla on the master branch

  * example (kolla): https://review.opendev.org/689731

* switch to use the new release of RDO on the new stable branch (master uses
  the delorean development packages)

  * example (kolla): https://review.opendev.org/651601

* switch to use the newly tagged container images (the branch for development
  mode on the new stable branch follows automatically since Victoria)

  * example (kolla-ansible): https://review.opendev.org/711214

* update previous release variables on master

  * example (kolla-ansible): https://review.opendev.org/650854

* search for TODOs/FIXMEs/NOTEs in the codebases describing tasks to be
  performed during the next release cycle

  * may include deprecations, code removal, etc.

  * these usually reference either the new cycle or the previous cycle;
    new cycle may be referenced using only the first letter (for example: V
    for Victoria).

After OpenStack Final Release
-----------------------------

* update dependencies for source images on master to use final releases:

  * ``./tools/version-check.py --openstack-release $SERIES``

  * example (kolla): https://review.opendev.org/651605/

RC2+
----

Further release candidates may be created on the stable branch as necessary in
a similar manner to RC1.

Final Releases
--------------

A release candidate may be promoted to a final release if it has no critical
bugs against it.

* create final release by submitting patches to the releases repository

  * example (kolla): TODO

  * example (kolla-ansible): TODO

* ensure static links to documentation are enabled

  * https://opendev.org/openstack/openstack-manuals/src/branch/master/www/project-data

  * example for Ussuri: https://review.opendev.org/739206

Stable Releases
===============

Stable branch releases should be made periodically for each supported stable
branch, no less than once every 45 days.

* check for new releases of dependencies

  * ``tools/version_check.py``

  * example (kolla): https://review.opendev.org/652674/

* create stable releases by submitting patches to the releases repository

  * follow SemVer guidelines

  * example (kolla): https://review.opendev.org/650411

  * example (kolla-ansible): https://review.opendev.org/650412

* mark milestones on Launchpad as released

* create new milestones on Launchpad for the next stable releases
