==================
Release Management
==================

This guide is intended to complement the `OpenStack releases site
<https://releases.openstack.org/>`__, and the project team guide's section on
`release management
<https://docs.openstack.org/project-team-guide/release-management.html>`__.

Team members make themselves familiar with the release schedule for the current
release, for example https://releases.openstack.org/train/schedule.html.

Concepts & Aims
===============

Release Model
-------------

As a deployment project, Kolla's release model differs from many other
OpenStack projects. Kolla follows the `cycle-trailing
<https://docs.openstack.org/project-team-guide/release-management.html#trailing-the-common-cycle>`__
release model, to allow time after the OpenStack coordinated release to wait
for distribution packages and support new features. This gives us three months
after the final release to prepare our final releases. Users are typically keen
to try out the new release, so we should aim to release as early as possible
while ensuring we have confidence in the release.

Overlapping Cycles
------------------

While the community may have the intention of releasing Kolla projects shortly
after the OpenStack coordinated release, there are typically issues that
prevent us from doing so, some of which may be outside of our control. Because
of this, it is normal for there to be a period where the community is working
on two releases - stabilising one for general availability, while developing
features for another.

Date Notation
-------------

The OpenStack release schedule uses an ``R-$N`` notation to describe the
timing of milestones and deadlines, where ``$N`` is the number of weeks until
the coordinated OpenStack release (**not** the Kolla general release). For a
typical 26 week release schedule, ``R-26`` is the first week, and ``R-0`` is
the week of the coordinated release. We use that notation here, extended to
include the period following a release as ``R+$N``.

.. _early-cycle-stability:

Early Cycle Stability
---------------------

Early in the OpenStack release cycle, as projects make larger changes, it is
common for the master branch to become less stable than normal. This can have a
negative impact Kolla community, who may be trying to complete the previous
release, or develop features for the current release. For this reason, from the
Xena cycle, we will continue to build and deploy the previous OpenStack release
for several weeks into the development cycle.

Feature Freeze
--------------

As with projects following the common release model, Kolla uses a feature
freeze period to allow the code to stabilise prior to release. There is no
official feature freeze date for the cycle-trailing model, but we aim to
freeze **three weeks** after the common feature freeze. During this time, no
features should be merged to the master branch, until the feature freeze is
lifted 3 weeks later.

Release Schedule
================

While we don't wish to repeat the OpenStack release documentation, we will
point out the high level schedule, and draw attention to areas where our
process is different.

Launchpad Admin
---------------

We track series (e.g. Stein) and milestones (e.g. 10.0.1) on Launchpad, and
target bugs and blueprints to these. Populating these in advance is necessary.
This needs to be done for each of the following projects:

* https://launchpad.net/kolla

* https://launchpad.net/kolla-ansible

* https://launchpad.net/ansible-collection-kolla

* https://launchpad.net/kayobe

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

R-23: Development begins
------------------------

Feature freeze ends on the master branch of Kolla projects. We continue to
build and deploy the previous release of OpenStack projects, as described in
:ref:`early-cycle-stability`.

* [all] Communicate end of feature freeze via IRC meeting and openstack-discuss
  mailing list.

* [kayobe] Switch ``openstack_release`` and ``override_checkout`` in Kayobe
  master branch to use the master branch of dependencies.

  .. note:: The IPA image still needs to use the previous release in order to
            be compatible with Ironic.

  * example: https://review.opendev.org/c/openstack/kayobe/+/791764

* [all] Search for TODOs/FIXMEs/NOTEs in the codebases describing tasks to be
  performed during the new release cycle

  * may include deprecations, code removal, etc.

  * these usually reference either the new cycle or the previous cycle;
    new cycle may be referenced using only the first letter (for example: V
    for Victoria).

R-17: Switch source images to current release
---------------------------------------------

* [kolla-ansible] Set ``previous_release`` variables to the previous release.

  * example: https://review.opendev.org/c/openstack/kolla-ansible/+/761835

* [kolla] Switch source images to use master branches.

  * This patch should include "Depends-On" in the commit message to the Kolla
    Ansible patch, to avoid skipping a release in upgrade tests
  * example: https://review.opendev.org/c/openstack/kolla/+/761742

* [kayobe] Set ``previous_release`` variables to the previous release.

  * example: https://review.opendev.org/c/openstack/kayobe/+/763375

R-8: Switch images to current release
-------------------------------------

.. note:: Debian does not provide repositories for the in-development release
          until much later in the cycle.

* [kolla] Switch Ubuntu images to use the current in-development release
  Ubuntu Cloud Archive (UCA) repository

  * example: https://review.opendev.org/c/openstack/kolla/+/782308

R-5: Cycle highlights deadline
------------------------------

* [all] Add `cycle highlights
  <https://docs.openstack.org/project-team-guide/release-management.html#cycle-highlights>`__
  when requested by the release team. They should be added to the deliverable
  file for the Kolla project, but also cover Kolla Ansible and Kayobe.

  * example: https://review.opendev.org/c/openstack/releases/+/779482

* [all] Check for new versions of infrastructure components

  * ansible (incl. kolla-toolbox)
  * ceph client libraries
  * fluentd (td-agent)
  * grafana
  * mariadb
  * opensearch
  * openvswitch/OVN
  * prometheus (incl. exporters)
  * rabbitmq/erlang

R-2: Feature freeze
-------------------

Feature freeze for Kolla deliverables begins. Feature freeze exceptions may be
granted within reason where two cores agree to review the code.

R-1: Prepare Kolla & Kolla Ansible for RC1 & stable branch creation
-------------------------------------------------------------------

As defined by the cycle-trailing release model, a stable branch is created at
the point of an RC1 release candidate.

Prior to creating an RC1 release candidate:

* [all] Test the code and fix (at a minimum) all critical bugs

* [all] The release notes for each project should be tidied up

  * this command is useful to list release notes added this cycle:

    * ``git diff --name-only origin/stable/<previous release> --
      releasenotes/``

    .. note::
       Release notes for backported changes (i.e. already present in the previous,
       stable branch) will not show in the output.

  * example (kolla): https://review.opendev.org/648677/

  * example (kolla-ansible): https://review.opendev.org/648685/

  * example (kayobe): https://review.opendev.org/c/openstack/kayobe/+/788432

* [kolla][kolla-ansible][ansible-collection-kolla] Mark bugs on Launchpad with
  the correct milestone

  * this command is useful to check for commits that fixed bugs:

    * ``git log origin/stable/<previous release>..origin/master | grep -i
      Closes-Bug``

* [kolla] Update ``OPENSTACK_RELEASE`` variable in ``kolla/common/config.py``
  to the name of the current in-development release

  * example: https://review.opendev.org/c/openstack/kolla/+/785500

* [kolla] Update versions of independently released projects on master:

  * ``./tools/version-check.py --openstack-release $SERIES
    --include-independent``

  * example: TODO

R-0: Kolla & Kolla Ansible RC1 & stable branch creation
-------------------------------------------------------

RC1 is the first release candidate, and also marks the point at which the
stable branch is cut.

.. note::

   Use the `new-release
   <https://releases.openstack.org/reference/using.html#using-new-release-command>`__
   tool for these activities.

* [kolla][kolla-ansible][ansible-collection-kolla] Create RC1 and stable
  branches by submitting patches to the releases repository

  * example: https://review.opendev.org/c/openstack/releases/+/786824

* [kolla][kolla-ansible][ansible-collection-kolla] Approve bot-proposed patches
  to master and the new stable branch

* [kolla][kolla-ansible] Ensure static links to documentation are enabled

  * https://opendev.org/openstack/openstack-manuals/src/branch/master/www/project-data

  * example: https://review.opendev.org/c/openstack/openstack-manuals/+/739206/

R-0: Prepare Kayobe for RC1 & stable branch creation
----------------------------------------------------

As defined by the cycle-trailing release model, a stable branch is created at
the point of an RC1 release candidate.

Some of these tasks depend on the existence of Kolla and Kolla Ansible stable
branches.

Prior to creating an RC1 release candidate:

* [kayobe] Synchronise with Kolla Ansible feature flags

  * Clone the Kolla Ansible repository, and run the Kayobe
    ``tools/kolla-feature-flags.sh`` script:

    .. code-block:: console

       tools/kolla-feature-flags.sh <path to kolla-ansible source>

  * Copy the output of the script, and replace the ``kolla_feature_flags`` list
    in ``ansible/roles/kolla-ansible/vars/main.yml``.

    The ``kolla.yml`` configuration file should be updated to match:

    .. code-block:: console

       tools/feature-flags.py

  * Copy the output of the script, and replace the list of ``kolla_enable_*``
    flags in ``etc/kayobe/kolla.yml``.

  * example: https://review.opendev.org/c/openstack/kayobe/+/787775

* [kayobe] Synchronise with Kolla Ansible inventory

  Clone the Kolla Ansible repository, and copy across any relevant changes. The
  Kayobe inventory is based on the ``ansible/inventory/multinode`` inventory,
  but split into 3 parts - top-level, components and services.

  * The top level inventory template is
    ``ansible/roles/kolla-ansible/templates/overcloud-top-level.j2``. It is
    heavily templated, and does not typically need to be changed. Look out for
    changes in the ``multinode`` inventory before the ``[baremetal]`` group.

  * The components inventory template is
    ``ansible/roles/kolla-ansible/templates/overcloud-components.j2``.

    This includes groups in the ``multinode`` inventory from the
    ``[baremetal]`` group down to the following text::

        # Additional control implemented here. These groups allow you to control which
        # services run on which hosts at a per-service level.

  * The services inventory template is
    ``ansible/roles/kolla-ansible/templates/overcloud-services.j2``.

    This includes groups in the ``multinode`` inventory from the following text to
    the end of the file::

        # Additional control implemented here. These groups allow you to control which
        # services run on which hosts at a per-service level.

    There are some small changes in this section which should be maintained.

  * example: https://review.opendev.org/c/openstack/kayobe/+/787775

* [kayobe] Update dependencies to upcoming release

  Prior to the release, we update the dependencies and upper constraints on the
  master branch to use the upcoming release. This is now quite easy to do,
  following the introduction of the ``openstack_release`` variable.

  * example: https://review.opendev.org/c/openstack/kayobe/+/787923

* [kayobe] Synchronise kayobe-config

  Ensure that configuration defaults in ``kayobe-config`` are in sync with
  those under ``etc/kayobe`` in ``kayobe``. This can be done via:

  .. code-block:: console

     rsync -a --delete kayobe/etc/kayobe/ kayobe-config/etc/kayobe

  Commit the changes and submit for review.

  * example: https://review.opendev.org/c/openstack/kayobe-config/+/787924

* [kayobe] Synchronise kayobe-config-dev

  Ensure that configuration defaults in ``kayobe-config-dev`` are in sync with
  those in ``kayobe-config``. This requires a little more care, since some
  configuration options have been changed from the defaults. Choose a method to
  suit you and be careful not to lose any configuration.

  Commit the changes and submit for review.

  * example: https://review.opendev.org/c/openstack/kayobe-config-dev/+/788426

R+1: Kayobe RC1 & stable branch creation
----------------------------------------

RC1 is the first release candidate, and also marks the point at which the
stable branch is cut.

.. note::

   Use the `new-release
   <https://releases.openstack.org/reference/using.html#using-new-release-command>`__
   tool for these activities.

* [kayobe] Create RC1 and stable branches by submitting patches to the releases
  repository

  * example: https://review.opendev.org/c/openstack/releases/+/788982

* [kayobe] Approve bot-proposed patches to master and the new stable branch

R+0 to R+13: Finalise stable branch
-----------------------------------

Several tasks are required to finalise the stable branch for release.

* [kolla-ansible][kayobe] Switch to use the new branch of
  ``ansible-collection-kolla`` in ``requirements.yml``.

  .. note:: This needs to be done on the stable branch.

* [kolla-ansible] Switch to use the newly tagged container images (the branch
  for development mode on the new stable branch follows automatically since
  Victoria)

  .. note:: This needs to be done on the stable branch.

  .. note:: This requires the images to have been published to quay.io with the
            new tag.

  * example: https://review.opendev.org/c/openstack/kolla-ansible/+/788292

* [kolla] Switch Debian images to use the Debian OpenStack repository
  for the new release

  .. note:: This needs to be done on the master branch and stable branch.

  * example: https://review.opendev.org/c/openstack/kolla/+/788304

R+0 to R+13: Further release candidates and final release
---------------------------------------------------------

Once the stable branches are finalised, further release candidates may be
created as necessary in a similar manner to RC1.

A release candidate may be promoted to a final release if it has no critical
bugs against it.

* [all] Create final release by submitting patches to the releases repository

  * example: https://review.opendev.org/c/openstack/releases/+/769328

* [all] Update openstack-manuals project-data for kolla + kolla-ansible

  * example: https://review.opendev.org/c/openstack/openstack-manuals/+/934349

After final release, projects enter the :ref:`stable-branch-lifecycle` with a
status of Maintained.

R+13 marks the 3 month deadline for the release of cycle-trailing projects.

.. _stable-branch-lifecycle:

Stable Branch Lifecycle
=======================

The lifecycle of stable branches in OpenStack is described in the `project team
guide <https://docs.openstack.org/project-team-guide/stable-branches.html>`__.
The current status of each branch is published on the `releases
<https://releases.openstack.org/>`__ site.

Maintained
----------

Releases should be made periodically for each maintained stable branch, no less
than once every 45 days. We try to make one release per month by having
a recurring topic for that in the first Kolla meeting each month.

* Create stable releases by submitting patches to the releases repository

  * follow SemVer guidelines, for simplicity consider always making minor
    version bumps

  * you can use the tooling from the requirements team to prepare the patches::

      git checkout -b kolla-stable-monthly
      for project in ansible-collection-kolla kayobe kolla kolla-ansible; do
          for rel in zed antelope bobcat; do
              tox -e venv -- new-release $rel $project feature
          done
      done
      git commit -am "Tag monthly kolla stable releases"
      git review -f

  * example release patch: https://review.opendev.org/c/openstack/releases/+/860521

Extended Maintenance (EM)
-------------------------

When a branch is entering EM, projects will make final releases. The release
team will propose tagging the Kolla deliverables as EM, but this should only be
done once all other dependent projects have made their final release, and final
Kolla releases have been made including those dependencies.

After a branch enters EM, we typically do the following:

* stop backporting fixes to the branch by default. Important fixes or those
  requested by community members may be merged if deemed appropriate
* stop publishing images to Quay.io
* stop actively maintaining CI

End of Life (EOL)
-----------------

Once a branch has been unmaintained (failing CI, no patches merged) for 6
months, it may be moved to EOL. Since this is done at different times for
different projects, send an email to openstack-discuss to keep the community
informed.
