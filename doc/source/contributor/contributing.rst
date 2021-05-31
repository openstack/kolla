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

Communication
~~~~~~~~~~~~~

IRC Channel
    ``#openstack-kolla`` (`channel logs`_) on `OFTC <http://oftc.net>`_

Weekly Meetings
    On Wednesdays at 15:00 UTC in the IRC channel (`meetings logs`_)

Mailing list (prefix subjects with ``[kolla]``)
    http://lists.openstack.org/pipermail/openstack-discuss/

Meeting Agenda
    https://wiki.openstack.org/wiki/Meetings/Kolla

Whiteboard (etherpad)
    Keeping track of CI gate status, release status, stable backports,
    planning and feature development status.
    https://etherpad.openstack.org/p/KollaWhiteBoard

.. _channel logs: http://eavesdrop.openstack.org/irclogs/%23openstack-kolla/
.. _meetings logs:  http://eavesdrop.openstack.org/meetings/kolla/

Contacting the Core Team
~~~~~~~~~~~~~~~~~~~~~~~~

The list in alphabetical order (on first name):

+-----------------------+---------------+------------------------------------+
| Name                  | IRC nick      | Email address                      |
+=======================+===============+====================================+
| `Christian Berendt`_  | berendt       | berendt@betacloud-solutions.de     |
+-----------------------+---------------+------------------------------------+
| `Dincer Celik`_       | osmanlicilegi | hello@dincercelik.com              |
+-----------------------+---------------+------------------------------------+
| `Eduardo Gonzalez`_   | egonzalez     | dabarren@gmail.com                 |
+-----------------------+---------------+------------------------------------+
| `Jeffrey Zhang`_      | Jeffrey4l     | jeffrey.zhang@99cloud.net          |
+-----------------------+---------------+------------------------------------+
| `Marcin Juszkiewicz`_ | hrw           | marcin.juszkiewicz@linaro.org      |
+-----------------------+---------------+------------------------------------+
| `Mark Goddard`_       | mgoddard      | mark@stackhpc.com                  |
+-----------------------+---------------+------------------------------------+
| `Michał Nasiadka`_    | mnasiadka     | mnasiadka@gmail.com                |
+-----------------------+---------------+------------------------------------+
| `Radosław Piliszek`_  | yoctozepto    | radoslaw.piliszek@gmail.com        |
+-----------------------+---------------+------------------------------------+
| `Surya Prakash`_      | spsurya       | singh.surya64mnnit@gmail.com       |
+-----------------------+---------------+------------------------------------+
| `Cao Yuan`_           | caoyuan       | cao.yuan@99cloud.net               |
+-----------------------+---------------+------------------------------------+

.. _Christian Berendt: https://launchpad.net/~berendt
.. _Dincer Celik: https://launchpad.net/~osmanlicilegi
.. _Eduardo Gonzalez: https://launchpad.net/~egonzalez90
.. _Jeffrey Zhang: https://launchpad.net/~jeffrey4l
.. _Marcin Juszkiewicz: https://launchpad.net/~hrw
.. _Mark Goddard: https://launchpad.net/~mgoddard
.. _Michał Nasiadka: https://launchpad.net/~mnasiadka
.. _Radosław Piliszek: https://launchpad.net/~yoctozepto
.. _Surya Prakash: https://launchpad.net/~confisurya
.. _Cao Yuan: https://launchpad.net/~caoi-yuan

The current effective list is also available from Gerrit:
https://review.opendev.org/#/admin/groups/460,members

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
+W. A release note is required on most changes as well. Release notes policy
is described in :ref:`its own section <release-notes>`.

Significant changes should have documentation and testing provided with them.

Project Team Lead Duties
~~~~~~~~~~~~~~~~~~~~~~~~

All common PTL duties are enumerated in the `PTL guide <https://docs.openstack.org/project-team-guide/ptl.html>`_.
Kolla-specific PTL duties are listed in `Kolla PTL guide <https://docs.openstack.org/kolla/latest/contributor/ptl-guide.html>`_.
