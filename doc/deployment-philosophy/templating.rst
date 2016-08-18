.. _templating:

================
Kolla Templating
================

Why not Template Customization?
===============================

The Kolla upstream community does not want to place key/value pairs in the
Ansible playbook configuration options that are not essential to obtaining
a functional deployment. If the Kolla upstream starts down the path of
templating configuration options, the Ansible configuration could conceivably
grow to hundreds of configuration key/value pairs which is unmanageable.
Further, as new versions of Kolla are released, there would be independent
customization available for different versions creating an unsupportable and
difficult to document environment. Finally, adding key/value pairs for
configuration options creates a situation in which development and release
cycles are required in order to successfully add new customizations.
Essentially templating in configuration options is not a scalable solution
and would result in an inability of the project to execute its mission.

Kolla's Solution to Customization
=================================

Rather than deal with the customization madness of templating configuration
options in Kolla's Ansible playbooks, Kolla eliminates all the inefficiencies
of existing deployment tools through a simple, tidy design: custom
configuration sections.

During deployment of an OpenStack service, a basic set of default configuration
options are merged with and overridden by custom ini configuration sections.
Kolla deployment customization is that simple! This does create a situation
in which the Operator must reference the upstream documentation if a
customization is desired in the OpenStack deployment. Fortunately the
configuration options documentation is extremely mature and well-formulated.

As an example, consider running Kolla in a virtual machine. In order to
launch virtual machines from Nova in a virtual environment, it is necessary
to use the QEMU hypervisor, rather than the KVM hypervisor. To achieve this
result, simply modify the file `/etc/kolla/config/nova/nova-compute.conf` and
add the contents::

    [libvirt]
    virt_type=qemu

After this change Kolla will use an emulated hypervisor with lower performance.
Kolla could have templated this commonly modified configuration option. If
Kolla starts down this path, the Kolla project could end with hundreds of
config options all of which would have to be subjectively evaluated for
inclusion or exclusion in the source tree.

Kolla's approach yields a solution which enables complete customization without
any upstream maintenance burden. Operators don't have to rely on a subjective
approval process for configuration options nor rely on a
development/test/release cycle to obtain a desired customization. Instead
operators have ultimate freedom to make desired deployment choices immediately
without the approval of a third party.
