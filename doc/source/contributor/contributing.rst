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
    In the IRC channel (`meeting information`_)

Mailing list (prefix subjects with ``[kolla]``)
    https://lists.openstack.org/pipermail/openstack-discuss/

Meeting Agenda
    :ref:`Meeting agenda <meeting-agenda>`

Whiteboard (etherpad)
    Keeping track of CI gate status, release status, stable backports,
    planning and feature development status.
    https://etherpad.openstack.org/p/KollaWhiteBoard

.. _channel logs: https://meetings.opendev.org/irclogs/%23openstack-kolla/
.. _meeting information: https://meetings.opendev.org/#Kolla_Team_Meeting

Contacting the Core Team
~~~~~~~~~~~~~~~~~~~~~~~~

In general it is suggested to use the above mentioned public communication
channels, but if you find that you need to contact someone from the Core team
directly, you can find the lists in Gerrit:

- `Kolla core team <https://review.opendev.org/admin/groups/kolla-core,members>`__
- `Kayobe core team <https://review.opendev.org/admin/groups/kayobe-core,members>`__

New Feature Planning
~~~~~~~~~~~~~~~~~~~~

New features are discussed on PTG, via IRC or mailing list (with [kolla]
prefix).

Task Tracking
~~~~~~~~~~~~~

Kolla family projects track tasks and bugs in Launchpad:

- `Kolla <https://bugs.launchpad.net/kolla>`__
- `Kolla Ansible <https://bugs.launchpad.net/kolla-ansible>`__
- `Ansible Collection Kolla <https://bugs.launchpad.net/ansible-collection-kolla>`__
- `Kayobe <https://bugs.launchpad.net/kayobe>`__

If you're looking for some smaller, easier work item to pick up and get started
on, search for the 'low-hanging-fruit' tag in the relevant project.

A more lightweight task tracking is done via etherpad - `Whiteboard <https://etherpad.openstack.org/p/KollaWhiteBoard>`__.

Reporting a Bug
~~~~~~~~~~~~~~~

You found an issue and want to make sure we are aware of it?
Please report it in the appropriate Launchpad project:

- `Kolla <https://bugs.launchpad.net/kolla>`__
- `Kolla Ansible <https://bugs.launchpad.net/kolla-ansible>`__
- `Ansible Collection Kolla <https://bugs.launchpad.net/ansible-collection-kolla>`__
- `Kayobe <https://bugs.launchpad.net/kayobe>`__

Note these are also used for task tracking.

Getting Your Patch Merged
~~~~~~~~~~~~~~~~~~~~~~~~~

Most changes proposed to Kolla require two +2 votes from core reviewers before
being approved and sent to the gate queue for merging. A release note is
required on most changes as well. Release notes policy
is described in :ref:`its own section <release-notes>`.

Significant changes should have documentation and testing provided with them.

To see an overview of in-progress patches, sorted into useful sections, you can
view the:

- `Kolla Review Dashboard <https://review.opendev.org/dashboard/?title=Kolla+Review+Dashboard&foreach=project%3Aopenstack%2Fkolla+status%3Aopen+NOT+label%3AWorkflow%3C%3D%2D1+NOT+label%3ACode%2DReview%3C%3D%2D2&High+priority+changes=label%3AReview%2DPriority%3D2&Priority+changes=label%3AReview%2DPriority%3D1&Feature+freeze=label%3AReview%2DPriority%3D%2D1&Stable+branch+backports=branch%3A%5Estable%2F.%2A+status%3Aopen+NOT+label%3AReview%2DPriority%3D%2D1&Small+things+%28%3C25+LOC%2C+limit+25%29+on+master+branch=delta%3A%3C%3D25+limit%3A25+NOT+label%3ACode%2DReview%2D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+Final+Approval+%28to+land+on+master+branch%29=NOT+label%3AWorkflow%3E%3D1+NOT+label%3AWorkflow%3C%3D%2D1+NOT+owner%3Aself+label%3ACode%2DReview%3E%3D2+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+revisit+%28You+were+a+reviewer+but+haven%27t+voted+in+the+current+revision%29=reviewer%3Aself+limit%3A50&Newer+%28%3C1wk%29+Open+Patches+%28limit+25%29+on+master+branch=%2Dage%3A1week+limit%3A25+NOT+label%3AWorkflow%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3ACode%2DReview%3E%3D2+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Older+%28%3E1wk%29+Open+Patches+Passing+Zuul+Tests+%28limit+50%29+on+master+branch=age%3A1week+limit%3A50+NOT+label%3AWorkflow%3E%3D1+NOT+label%3ACode%2DReview%3C%3D%2D1+NOT+label%3ACode%2DReview%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster>`__

- `Kolla Ansible Review Dashboard <https://review.opendev.org/dashboard/?title=Kolla%2DAnsible+Review+Dashboard&foreach=project%3Aopenstack%2Fkolla%2Dansible+status%3Aopen+NOT+label%3AWorkflow%3C%3D%2D1+NOT+label%3ACode%2DReview%3C%3D%2D2&High+priority+changes=label%3AReview%2DPriority%3D2&Priority+changes=label%3AReview%2DPriority%3D1&Feature+freeze=label%3AReview%2DPriority%3D%2D1&Stable+branch+backports=branch%3A%5Estable%2F.%2A+status%3Aopen+NOT+label%3AReview%2DPriority%3D%2D1&Small+things+%28%3C25+LOC%2C+limit+25%29+on+master+branch=delta%3A%3C%3D25+limit%3A25+NOT+label%3ACode%2DReview%2D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+Final+Approval+%28to+land+on+master+branch%29=NOT+label%3AWorkflow%3E%3D1+NOT+label%3AWorkflow%3C%3D%2D1+NOT+owner%3Aself+label%3ACode%2DReview%3E%3D2+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+revisit+%28You+were+a+reviewer+but+haven%27t+voted+in+the+current+revision%29=reviewer%3Aself+limit%3A50&Newer+%28%3C1wk%29+Open+Patches+%28limit+25%29+on+master+branch=%2Dage%3A1week+limit%3A25+NOT+label%3AWorkflow%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3ACode%2DReview%3E%3D2+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Older+%28%3E1wk%29+Open+Patches+Passing+Zuul+Tests+%28limit+50%29+on+master+branch=age%3A1week+limit%3A50+NOT+label%3AWorkflow%3E%3D1+NOT+label%3ACode%2DReview%3C%3D%2D1+NOT+label%3ACode%2DReview%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster>`__

- `Ansible Collection Kolla Review Dashboard <https://review.opendev.org/dashboard/?title=ansible%2Dcollection%2Dkolla+Review+Dashboard&foreach=project%3Aopenstack%2Fansible%2Dcollection%2Dkolla+status%3Aopen+NOT+label%3AWorkflow%3C%3D%2D1+NOT+label%3ACode%2DReview%3C%3D%2D2&High+priority+changes=label%3AReview%2DPriority%3D2&Priority+changes=label%3AReview%2DPriority%3D1&Feature+freeze=label%3AReview%2DPriority%3D%2D1&Stable+branch+backports=branch%3A%5Estable%2F.%2A+status%3Aopen+NOT+label%3AReview%2DPriority%3D%2D1&Small+things+%28%3C25+LOC%2C+limit+25%29+on+master+branch=delta%3A%3C%3D25+limit%3A25+NOT+label%3ACode%2DReview%2D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+Final+Approval+%28to+land+on+master+branch%29=NOT+label%3AWorkflow%3E%3D1+NOT+label%3AWorkflow%3C%3D%2D1+NOT+owner%3Aself+label%3ACode%2DReview%3E%3D2+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+revisit+%28You+were+a+reviewer+but+haven%27t+voted+in+the+current+revision%29=reviewer%3Aself+limit%3A50&Newer+%28%3C1wk%29+Open+Patches+%28limit+25%29+on+master+branch=%2Dage%3A1week+limit%3A25+NOT+label%3AWorkflow%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3ACode%2DReview%3E%3D2+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Older+%28%3E1wk%29+Open+Patches+Passing+Zuul+Tests+%28limit+50%29+on+master+branch=age%3A1week+limit%3A50+NOT+label%3AWorkflow%3E%3D1+NOT+label%3ACode%2DReview%3C%3D%2D1+NOT+label%3ACode%2DReview%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster>`__

- `Kayobe Review Dashboard <https://review.opendev.org/dashboard/?title=Kayobe+Review+Dashboard&foreach=%28project%3Aopenstack%2Fkayobe+OR+project%3Aopenstack%2Fkayobe%2Dconfig+OR+project%3Aopenstack%2Fkayobe%2Dconfig%2Ddev%29+status%3Aopen+NOT+label%3ACode%2DReview%3C%3D%2D2+NOT+label%3AWorkflow%3C%3D%2D1&High+priority+changes=label%3AReview%2DPriority%3D2&Priority+changes=label%3AReview%2DPriority%3D1&Feature+freeze=label%3AReview%2DPriority%3D%2D1&Stable+branch+backports=branch%3A%5Estable%2F.%2A+status%3Aopen+NOT+label%3AReview%2DPriority%3D%2D1&Small+things+%28%3C25+LOC%2C+limit+25%29+on+master+branch=delta%3A%3C%3D25+limit%3A25+NOT+label%3ACode%2DReview%2D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+Final+Approval+%28to+land+on+master+branch%29=NOT+label%3AWorkflow%3E%3D1+NOT+label%3AWorkflow%3C%3D%2D1+NOT+owner%3Aself+label%3ACode%2DReview%3E%3D2+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Needs+revisit+%28You+were+a+reviewer+but+haven%27t+voted+in+the+current+revision%29=reviewer%3Aself+limit%3A50&Newer+%28%3C1wk%29+Open+Patches+%28limit+25%29+on+master+branch=%2Dage%3A1week+limit%3A25+NOT+label%3AWorkflow%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3ACode%2DReview%3E%3D2+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster&Older+%28%3E1wk%29+Open+Patches+Passing+Zuul+Tests+%28limit+50%29+on+master+branch=age%3A1week+limit%3A50+NOT+label%3AWorkflow%3E%3D1+NOT+label%3ACode%2DReview%3C%3D%2D1+NOT+label%3ACode%2DReview%3E%3D1+label%3AVerified%3E%3D1%2Czuul+NOT+label%3AReview%2DPriority%3D%2D1+branch%3Amaster>`__

.. note::

   If you feel that your change is getting overlooked, reach out via
   :ref:`preferred communication methods <communication>` to let us know.

Project Team Lead Duties
~~~~~~~~~~~~~~~~~~~~~~~~

All common PTL duties are enumerated in the `PTL guide <https://docs.openstack.org/project-team-guide/ptl.html>`_.
Kolla-specific PTL duties are listed in `Kolla PTL guide <https://docs.openstack.org/kolla/latest/contributor/ptl-guide.html>`_.
