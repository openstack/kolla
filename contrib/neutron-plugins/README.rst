contrib/neutron-plugins directory
=================================

This directory contains example plugin definitions for neutron-base, to
be included in the kolla-build.conf (ini file with kolla-build
configuration) when using source type builds.

In case of binary builds - please see template_override j2 files.

Please read the main Kolla documentation on plugins for details.
These should work simply by pasting them into the config file.
You may want to adjust the filename to match the branch you are
interested in, however.
