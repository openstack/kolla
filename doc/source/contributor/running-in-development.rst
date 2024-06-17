.. _running-in-development:

==================================
Running Kolla Build in development
==================================

The recommended way to run in development
-----------------------------------------

To clone the repository and install the package
in development mode, run the following commands:


.. code-block:: console

    git clone https://opendev.org/openstack/kolla.git
    cd kolla
    python3 -m venv ~/path/to/venv
    source ~/path/to/venv/bin/activate
    python3 -m pip install --editable .
    kolla-build ...
