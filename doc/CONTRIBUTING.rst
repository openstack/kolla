.. _CONTRIBUTING:

=================
How To Contribute
=================

Basics
======

#. Our source code is hosted on `OpenStack GitHub`_, but pull requests submitted
   through GitHub will be ignored. Bugs should be filed on launchpad_,
   not GitHub.

#. Please follow OpenStack `Gerrit Workflow`_ to to contribute to Kolla.

#. Note the branch you're proposing changes to. ``master`` is the current focus
   of development. Kolla project has a strict policy of only allowing backports
   in ``stable/branch``, unless when not applicable. A bug in a ``stable/branch``
   will first have to be fixed in ``master``.

#. Please file a launchpad_ blueprint for any significant code change and a bug
   for any significant bug fix or add a TrivialFix tag for simple changes.
   See how to reference a bug or a blueprint in the commit message here_

#. TrivialFix tags or bugs are not required for documentation changes.

.. _OpenStack GitHub: https://github.com/openstack/kolla
.. _Gerrit Workflow: http://docs.openstack.org/infra/manual/developers.html#development-workflow
.. _launchpad: https://bugs.launchpad.net/kolla
.. _here: https://wiki.openstack.org/wiki/GitCommitMessages

Development Environment
=======================

#. Please follow our `quickstart`_ to deploy your environment and test your
  changes.

.. _quickstart: http://docs.openstack.org/developer/kolla/quickstart.html
