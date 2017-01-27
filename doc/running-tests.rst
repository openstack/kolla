.. _running-tests:

=============
Running tests
=============

Kolla contains a suite of tests in the
``tests`` and ``kolla/tests`` directories.

Any proposed code change in gerrit is automatically rejected by the OpenStack
Jenkins server [#f1]_ if the change causes test failures.

It is recommended for developers to run the test suite before submitting patch
for review. This allows to catch errors as early as possible.

Preferred way to run the tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The preferred way to run the unit tests is using ``tox``. It executes tests in
isolated environment, by creating separate virtualenv and installing
dependencies from the ``requirements.txt`` and ``test-requirements.txt`` files,
so the only package you install is ``tox`` itself:

.. code-block:: console

    $ pip install tox

See `the unit testing section of the Testing wiki page`_ for more information.
Following are some simple examples.

To run the Python 2.7 tests:

.. code-block:: console

    $ tox -e py27

To run the style tests:

.. code-block:: console

    $ tox -e pep8

To run multiple tests separate items by commas:

.. code-block:: console

    $ tox -e py27,py34,pep8

.. _the unit testing section of the Testing wiki page: https://wiki.openstack.org/wiki/Testing#Unit_Tests

Running a subset of tests
-------------------------

Instead of running all tests, you can specify an individual directory, file,
class or method that contains test code, i.e. filter full names of tests by a
string.

To run the tests located only in the ``kolla/tests``
directory use:

.. code-block:: console

    $ tox -e py27 kolla.tests

To run the tests of a specific file say ``kolla/tests/test_kolla_docker.py``:

.. code-block:: console

    $ tox -e py27 test_kolla_docker

To run the tests in the ``ModuleArgsTest`` class in
the ``kolla/tests/test_kolla_docker.py`` file:

.. code-block:: console

    $ tox -e py27 test_kolla_docker.ModuleArgsTest

To run the ``ModuleArgsTest.test_module_args`` test method in
the ``kolla/tests/test_kolla_docker.py`` file:

.. code-block:: console

    $ tox -e py27 test_kolla_docker.ModuleArgsTest.test_module_args


Coverage Report Generation
--------------------------

In order to get coverage report for Kolla, run the below command.

.. code-block:: console

    $ tox -e cover

Debugging unit tests
------------------------

In order to break into the debugger from a unit test we need to insert
a breaking point to the code:

.. code-block:: python

  import pdb; pdb.set_trace()

Then run ``tox`` with the debug environment as one of the following::

  tox -e debug
  tox -e debug test_file_name.TestClass.test_name

For more information see the `oslotest documentation
<http://docs.openstack.org/developer/oslotest/features.html#debugging-with-oslo-debug-helper>`_.


.. rubric:: Footnotes

.. [#f1] See http://docs.openstack.org/infra/system-config/jenkins.html
