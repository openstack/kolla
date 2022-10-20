.. _release-notes:

=============
Release notes
=============

Introduction
~~~~~~~~~~~~

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

When a release note is required:

- ``feature`` - best included with docs change (if separate from the code)
- ``user impacting`` - to improve visibility of the change for users

Remember release notes are mostly for end users which, in case of Kolla,
are OpenStack administrators/operators.
In case of doubt, the core team will let you know what is required.

To add a release note, run the following command:

.. code-block:: console

   tox -e venv -- reno new <summary-line-with-dashes>

All release notes can be inspected by browsing ``releasenotes/notes``
directory. Further on this page we show reno templates, examples and how to
make use of them.

.. note::

  The term `release note` is often abbreviated to `reno` as it is the name of
  the tool that is used to manage the release notes.

To generate renos in HTML format in ``releasenotes/build``, run:

.. code-block:: console

   tox -e releasenotes

Note this requires the release note to be tracked by ``git`` so you
have to at least add it to the ``git``'s staging area.

The release notes are linted in the CI system. To lint locally, run:

.. code-block:: console

   tox -e doc8

The above lints all of documentation at once.

Templates and examples
~~~~~~~~~~~~~~~~~~~~~~

All approved release notes end up being published on a dedicated site:

   https://docs.openstack.org/releasenotes/kolla/

When looking for examples, it is advised to consider browsing the page above
for a similar type of change and then comparing with their source
representation in ``releasenotes/notes``.

The sections below give further guidelines. Please try to follow them but note
they are not set in stone and sometimes a different wording might be more
appropriate. In case of doubt, the core team will be happy to help.

Features
--------

Template
++++++++

.. path releasenotes/templates/feature.yml
.. code-block:: yaml

   ---
   features:
     - |
       Implements [some feature].
       [Can be described using multiple sentences if necessary.]
       [Limitations worth mentioning can be included as well.]
       `Blueprint [blueprint id] <https://blueprints.launchpad.net/kolla/+spec/[blueprint id]>`__

.. note::

  The blueprint can be mentioned even if the change implements it only
  partially. This can be emphasised by preceding the ``Blueprint`` word by
  ``Partial``. See the example below.

Example
+++++++

Implementing blueprint with id `letsencrypt-https`, we use ``reno`` to generate
the scaffolded file:

.. code-block:: console

   tox -e venv -- reno new --from-template releasenotes/templates/feature.yml blueprint-letsencrypt-https

.. note::

  Since we don't require blueprints for simple features, it is allowed to
  make up a blueprint-id-friendly string (like in the example here) ad-hoc
  for the proposed feature. Please then skip the ``blueprint-`` prefix to
  avoid confusion.

And then fill it out with the following content:

.. code-block:: yaml

   ---
   features:
     - |
       Implements support for hassle-free integration with Let's Encrypt.
       The support is limited to operators in the underworld.
       For more details check the TLS docs of Kolla.
       `Partial Blueprint letsencrypt-https <https://blueprints.launchpad.net/kolla/+spec/letsencrypt-https>`__

.. note::

  The example above shows how to introduce a limitation. The limitation may be
  lifted in the same release cycle and it is OK to mention it nonetheless.
  Release notes can be edited later as long as they have not been shipped in
  an existing release or release candidate.

Fixes
-----

Template
++++++++

.. path releasenotes/templates/fix.yml
.. code-block:: yaml

   ---
   fixes:
     - |
       Fixes [some bug].
       [Can be described using multiple sentences if necessary.]
       [Possibly also giving the previous behaviour description.]
       `LP#[bug number] <https://launchpad.net/bugs/[bug number]>`__

Example
+++++++

Fixing bug number `1889611`, we use ``reno`` to generate the scaffolded file:

.. code-block:: console

   tox -e venv -- reno new --from-template releasenotes/templates/fix.yml bug-1889611

And then fill it out with the following content:

.. code-block:: yaml

   ---
   fixes:
     - |
       Fixes ``deploy-containers`` action missing for the Masakari role.
       `LP#1889611 <https://launchpad.net/bugs/1889611>`__
