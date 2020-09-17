.. _running-in-development:

==================================
Running Kolla Build in development
==================================

The recommended way to run in development
-----------------------------------------

The preferred way to run kolla-build for development is using ``tox``.
Run the following from inside the repository:

.. code-block:: console

    tox -e venv -- kolla-build ...

The alternative way to run in development
-----------------------------------------

Sometimes, developers prefer to manage their venvs themselves. This is also
possible. Remember to install in editable mode (``-e``). Run the following from
inside the repository:

.. code-block:: console

    python3 -m venv ~/path/to/venv
    source ~/path/to/venv/bin/activate
    python3 -m pip install -e .
    kolla-build ...
