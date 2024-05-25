=========
PTL Guide
=========

This is just a reference guide that a PTL may use as an aid, if they choose.
It is meant to complement the `official PTL guide
<https://docs.openstack.org/project-team-guide/ptl.html>`__, and is laid out in
rough chronological order.

Some or all of these tasks may be delegated to other team members.

New PTL
=======

* Update the kolla meeting chair

  * https://opendev.org/opendev/irc-meetings/src/branch/master/meetings/kolla-team-meeting.yaml

* Update the team wiki

  * https://wiki.openstack.org/wiki/Kolla#Active_Contributors

* Get acquainted with the release schedule, bearing in mind that Kolla is a
  cycle-trailing project

  * Example: https://releases.openstack.org/train/schedule.html

Open Infrastructure Summit
==========================

Ideally the Kolla PTL will be able to attend the summit. If not, try to arrange
for another member of the core team to represent the team. Good interaction
with the community at these events is crucial to encourage upstream
involvement, onboard new users, collect feedback and for the perceived health
of the project.

* Create a summit planning etherpad and alert about it in the kolla IRC meeting
  and openstack-discuss mailing list

  * Example: https://etherpad.openstack.org/p/kolla-train-summit

* Gather ideas for forum sessions

  * Example: user feedback & roadmap, design sessions

* Prepare the project update presentation. Enlist help of others

* Prepare the on-boarding session materials. Enlist help of others

* Represent and promote the project while at the summit

Project Team Gathering (PTG)
============================

Some of the Kolla team may decide to meet in person at the Project Team
Gathering (PTG). Alternatively, they may decide to host a virtual PTG at a
different time if there is not a critical mass of contributors attending the
PTG.

* Create PTG planning etherpad and alert about it in the
  kolla IRC meeting and openstack-discuss mailing list

  * Example: https://etherpad.openstack.org/p/kolla-train-ptg

* Run sessions at the PTG

* Have a discussion about priorities for the upcoming release cycle at the PTG

* Sign up for group photo at the PTG (if applicable)

* Standard PTG topics:

  * Required distribution upgrades (e.g. new Ubuntu LTS release)
  * Ansible version bump
  * Infrastructure services/packages updates (e.g. RabbitMQ/Erlang upgrades)
  * Services that need to be deprecated/removed (e.g. unmaintained projects)

After Summit & PTG
==================

* Send session summaries to the openstack-discuss mailing list

* Update the `Kolla whiteboard
  <https://etherpad.openstack.org/p/KollaWhiteBoard>`__ with decided priorities
  for the upcoming release cycle

Day to Day
==========

* Subscribe to the kolla projects on Launchpad to receive all bug and blueprint
  updates.

* :doc:`Triage new bugs <bug-triage>`

* Monitor the status of the CI system for all supported branches. Fix issues
  that break the gate

* Chair the IRC meetings

* Be available in IRC to help new and existing contributors

* Keep track of the progress of cycle priorities

* Monitor the core team membership, mentor potential cores

Release Management
==================

* Follow the project's :doc:`release management <release-management>` guide

* Use the IRC meeting and/or mailing list to communicate release schedule to
  the team who might not be so famailiar with it

Handing Over
============

* Support the new PTL in their new role. Try to remember the issues you
  encountered

* Update this page with any useful information you have learned
