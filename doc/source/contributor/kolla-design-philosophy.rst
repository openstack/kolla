=======================
Kolla design philosophy
=======================

This page aims to explain the design choices that have been made
in the Kolla projects (the main Kolla project for building the images
as well as all subprojects aimed at deploying them).

It is written down mostly for potential contributors but may be a good
guideline for anyone using and integrating with Kolla projects as it gives
an overview of what the preferred approach is. As noted, this is of great
interest to contributors because it might explain why certain changes will
get rejected and why some others will need a remake in order to be
accepted.

This page is likely an always-in-progress, living document.
Please reach out to the team via the mailing list or the IRC channel to
discuss the rules noted here, see our docs on
:ref:`communication <communication>` for details.

Do not own the deployed services' config defaults (unless necessary)
--------------------------------------------------------------------

In Kolla, we try not to own service config and its defaults.
We believe the upstream services know best what works for them by default.

This rule is overridden when a certain config option needs to be orchestrated
among multiple services or otherwise needs to agree with certain other
assumptions made in the environment. The notable exceptions here are the
basic addressing of services and Keystone credentials.

Prefer documented configuration via config overrides
----------------------------------------------------

... as opposed to new in-Ansible variables.

This plays nicely with the config overrides capabilities of Kolla Ansible
which let users easily customise the services' config to their hearts'
contents regardless of what Kolla Ansible offers via Ansible variables.

The reasoning behind this rule is that it lowers the maintenance burden
yet it does not handicap the users - they can control every last detail
of their config.

One of the (not necessarily planned) side-effects of this is that users'
config overrides are not locked-in for Kolla Ansible and can relatively
easily be reused in other configuration systems.
