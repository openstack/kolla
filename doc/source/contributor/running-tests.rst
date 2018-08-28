.. _running-tests:

=============
Running tests
=============

Kolla contains a suite of tests in the
``tests`` and ``kolla/tests`` directories.

Any proposed code change in gerrit is automatically rejected by the OpenStack
`Jenkins Job Builder <https://docs.openstack.org/infra/system-config/jjb.html>`__
if the change causes test failures.

It is recommended for developers to run the test suite before submitting patch
for review. This allows to catch errors as early as possible.

Preferred way to run the tests
------------------------------

The preferred way to run the unit tests is using ``tox``. It executes tests in
isolated environment, by creating separate virtualenv and installing
dependencies from the ``requirements.txt`` and ``test-requirements.txt`` files,
so the only package you install is ``tox`` itself:

.. code-block:: console

    pip install tox

.. end

See the `unit testing <https://wiki.openstack.org/wiki/Testing#Unit_Tests>`__
section of the Testing wiki page for more information.
Following are some simple examples.

To run the Python 2.7 tests:

.. code-block:: console

    tox -e py27

.. end

To run the style tests:

.. code-block:: console

    tox -e pep8

.. end

To run multiple tests separate items by commas:

.. code-block:: console

    tox -e py27,py35,pep8

.. end

Running a subset of tests
-------------------------

Instead of running all tests, you can specify an individual directory, file,
class or method that contains test code, for example, filter full names of
tests by a string.

To run the tests located only in the ``kolla/tests`` directory:

.. code-block:: console

    tox -e py27 kolla.tests

.. end

To run the tests of a specific file say ``kolla/tests/test_set_config.py``:

.. code-block:: console

    tox -e py27 test_set_config

.. end

To run the tests in the ``ConfigFileTest`` class in
the ``kolla/tests/test_set_config.py`` file:

.. code-block:: console

    tox -e py27 test_set_config.ConfigFileTest

.. end

To run the ``ConfigFileTest.test_delete_path_not_exists`` test method in
the ``kolla/tests/test_set_config.py`` file:

.. code-block:: console

    tox -e py27 test_set_config.ConfigFileTest.test_delete_path_not_exists

.. end

Coverage Report Generation
--------------------------

In order to get coverage report for Kolla, run the below command.

.. code-block:: console

    tox -e cover

.. end

Debugging unit tests
--------------------

In order to break into the debugger from a unit test we need to insert
a breaking point to the code:

.. code-block:: python

  import pdb; pdb.set_trace()

.. end

Then run :command:`tox` with the debug environment as one of the following:

.. code-block:: console

   tox -e debug
   tox -e debug test_file_name.TestClass.test_name

.. end

For more information see the `oslotest documentation
<https://docs.openstack.org/oslotest/latest/user/features.html#debugging-with-oslo-debug-helper>`_.


.. rubric:: Footnotes
