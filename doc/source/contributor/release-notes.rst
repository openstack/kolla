.. _release-notes:

=============
Release notes
=============

Kolla uses the following release notes sections:

- ``features`` --- for new features or functionality; these should ideally
  refer to the blueprint being implemented;
- ``fixes`` --- for fixes closing bugs; these must refer to the bug being
  closed;
- ``upgrade`` --- for notes relevant when upgrading from previous version;
  these should ideally be added only between major versions; required when
  the proposed change affects behaviour in a non-backwards compatible way or
  generally changes something impactful;
- ``deprecations`` --- to track deprecated features; relevant changes may
  consist of only the commit message and the release note;
- ``prelude`` --- filled in by the PTL before each release or RC.

Other release note types may be applied per common sense.
Each change should include a release note unless being a ``TrivialFix``
change or affecting only docs or CI. Such changes should `not` include
a release note to avoid confusion.
Remember release notes are mostly for end users which, in case of Kolla,
are OpenStack administrators/operators.
In case of doubt, the core team will let you know what is required.

To add a release note, run the following command:

.. code-block:: console

   tox -e venv -- reno new <summary-line-with-dashes>

All release notes can be inspected by browsing ``releasenotes/notes``
directory.

To generate release notes in HTML format in ``releasenotes/build``, run:

.. code-block:: console

   tox -e releasenotes

Note this requires the release note to be tracked by ``git`` so you
have to at least add it to the ``git``'s staging area.
