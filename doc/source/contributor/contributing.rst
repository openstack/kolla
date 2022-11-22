============================
So You Want to Contribute...
============================

For general information on contributing to OpenStack, please check out the
`contributor guide <https://docs.openstack.org/contributors/>`_ to get started.
It covers all the basics that are common to all OpenStack projects: the
accounts you need, the basics of interacting with our Gerrit review system,
how we communicate as a community, etc.

Below will cover the more project specific information you need to get started
with Kolla.

Basics
~~~~~~

The source repository for this project can be found at:

   https://opendev.org/openstack/kolla

.. _communication:

Communication
~~~~~~~~~~~~~

IRC Channel
    ``#openstack-kolla`` (`channel logs`_) on `OFTC <http://oftc.net>`_

Weekly Meetings
    On Wednesdays at 14:00 UTC in the IRC channel (`meetings logs`_)

Mailing list (prefix subjects with ``[kolla]``)
    https://lists.openstack.org/pipermail/openstack-discuss/

Meeting Agenda
    :ref:`Meeting agenda <meeting-agenda>`

Whiteboard (etherpad)
    Keeping track of CI gate status, release status, stable backports,
    planning and feature development status.
    https://etherpad.openstack.org/p/KollaWhiteBoard

.. _channel logs: https://meetings.opendev.org/irclogs/%23openstack-kolla/
.. _meetings logs:  https://meetings.opendev.org/meetings/kolla/

Contacting the Core Team
~~~~~~~~~~~~~~~~~~~~~~~~

In general it is suggested to use the above mentioned public communication
channels, but if you find the you need to contact someone from the Core team
directly, you can find the lists in Gerrit:

- kolla-core https://review.opendev.org/admin/groups/28d5dccfccc125b3963f76ab67e256501565d52b,members
- kolla-ansible-core https://review.opendev.org/admin/groups/cfd61289b70f00206797b035aa0bd7adfccf4be2,members
- kayobe-core https://review.opendev.org/admin/groups/361e28280e3a06be2997a5aa47a8a11d3a8fb9b9,members

New Feature Planning
~~~~~~~~~~~~~~~~~~~~

New features are discussed via IRC or mailing list (with [kolla] prefix).
Kolla project keeps blueprints in `Launchpad <https://blueprints.launchpad.net/kolla>`__.
Specs are welcome but not strictly required.

Task Tracking
~~~~~~~~~~~~~

Kolla project tracks tasks in `Launchpad <https://bugs.launchpad.net/kolla>`__.
Note this is the same place as for bugs.

If you're looking for some smaller, easier work item to pick up and get started
on, search for the 'low-hanging-fruit' tag.

A more lightweight task tracking is done via etherpad - `Whiteboard <https://etherpad.openstack.org/p/KollaWhiteBoard>`__.

Reporting a Bug
~~~~~~~~~~~~~~~

You found an issue and want to make sure we are aware of it? You can do so
on `Launchpad <https://bugs.launchpad.net/kolla>`__.
Note this is the same place as for tasks.

Getting Your Patch Merged
~~~~~~~~~~~~~~~~~~~~~~~~~

Most changes proposed to Kolla require two +2 votes from core reviewers before
being approved and sent to the gate queue for merging. A release note is
required on most changes as well. Release notes policy
is described in :ref:`its own section <release-notes>`.

Significant changes should have documentation and testing provided with them.

Project Team Lead Duties
~~~~~~~~~~~~~~~~~~~~~~~~

All common PTL duties are enumerated in the `PTL guide <https://docs.openstack.org/project-team-guide/ptl.html>`_.
Kolla-specific PTL duties are listed in `Kolla PTL guide <https://docs.openstack.org/kolla/latest/contributor/ptl-guide.html>`_.
