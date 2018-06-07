===========================
MariaDB Backup and Recovery
===========================

Existing BP: https://blueprints.launchpad.net/kolla/+spec/database-backup-recovery

This blueprint attempts to outline the introduction of backup and recovery
features in Kolla, for data hosted in MariaDB.  It aims to do so by
introducing tooling and options that are proven in deployments elsewhere, and
with a degree of flexibility which facilitates integration with existing
solutions.

Problem description
===================

Kolla currently lacks an easy way for an operator to be able to take a backup
of some or all of their MariaDB databases.  Unrecoverable loss of data hosted
in MariaDB can have disastrous consequences, so a feature which eases the
introduction of a sensible backup and restore routine into an OpenStack
operator's life is a worthwhile endeavour.

As backups are no use unless you can restore them, this solution should also
include a feature - or at the very least, a documented set of steps - for an
operator to be able to easily perform a restore and test the validity of their
data.

As stated in the BP, general backup strategy should be considered out-of-scope
as it's likely that each individual or organisation deploying OpenStack will
have their own opinion on what should be done and the frequency with which
these things should be performed.  However, Kolla should at least offer a way
to expose the necessary mechanisms to facilitate existing strategies.

Use cases
---------

- As an operator, I wish to make an ad-hoc (on demand) backup of some or all
  MariaDB databases, prior to making any manual changes;

- As an operator, I'd like to include my MariaDB database(s) in the scope of my
  regularly scheduled backups, and would like to be able to do so via Kolla;

- As an operator, I want to be able to restore my database(s) to a particular
  point in time following a failed upgrade or a stray manual query.

For the first two use-cases, full and incremental backup options should be
available.

Proposed change
===============

There are several considerations as part of this proposed change.  There's the
tooling necessary to perform a backup, the ability to schedule backups, and the
requirement to transfer the data elsewhere.

Backup Tooling
--------------

The linked Blueprint linked mentions the fact that there are several tools
available which facilitate MariaDB backup (and restore).  The most common is
`mysqldump`, as this is included as standard with every installation and can
be used to take a consistent backup of some or all databases.  However, taking
a backup with this tool has some limitations, chief amongst which is that it
can have a significant performance impact when taking backups in a way that
doesn't lock the database for the duration.

Instead, this proposed change will make use of Percona's XtraBackup tool, which
has been designed specifically for 'hot-backups' avoiding locking and heavy
performance impact. Because of the way XtraBackup functions, it also
facilitates a simpler test / restore procedure as these are physical copies of
the underlying database files, meaning a new instance of MariaDB can be spun up
against these in order to test.

Percona provides pre-packaged binaries for this tool via their own mirrors in
all of the major distributions supported by Kolla.

To implement this, this change will introduce a new Kolla container image
hosting the XtraBackup binary plus dependencies necessary to be able to
connect to MariaDB and retrieve data from some or all of the databases.

A Kolla-Ansible role will be created which will define tasks to:

* Establish the necessary backup-specific credentials;

* Start a container from this image with an associated volume and perform a
  full backup if no previous data exists, or an incremental backup if there is
  existing data.  See below for a suggested default schedule.

The backup data will reside in a dedicated Docker volume.  This can then be
used to facilitate transfer of the data elsewhere (i.e mounted by another
container with the tooling necessary to encrypt and upload) or be exported to
another host for testing.

Backups will be performed by default locally, that is on the node currently
running MariaDB, or on the designated master in a Galera cluster.  However, it
should be possible to nominate any node which has access to either the internal
API address or the database node directly.  It's up to the operator to choose
which mode is best for them, as there are a number of different considerations
and trade-offs to make.  A new configuration option should be introduced to
facilitate selection from a member of the MariaDB group.

Scheduling
----------

Automatic scheduling of backups should be disabled by default, but Kolla could
provide a mechanism to facilitate this if it's an operational requirement.

The approach described above doesn't introduce a new, persist container.
Instead, it would be one which runs on demand and produces the target backup
files.

Scheduling could be handled by changing this approach so that the container
runs in perpetuity, with the localised backup scripts being triggered by cron
according to a suggested (but configurable) default schedule.  A proposed
schedule would be:

  * A full backup every 24 hours;
  * An incremental backup every hour;
  * Full backups are retained for two weeks;
  * Incremental backups are retained for 24 hours.

Alternatively, backups could be triggered by another container or service
running on the host.

Archival
--------

Another tool is required to manage the backup lifecycle.  This is currently
considered out of scope.

Backup Restore
--------------

By targeting a discrete Docker volume for the data that's been backed up,
facilitating a restore is relatively straightforward.  Automating this is
currently out of scope, but this piece of work should include an example
procedure for how to handle this volume and access the data that's been backed
up.

Security impact
---------------

Implementation of this BP will require the introduction of a dedicated backup
role within MariaDB in order to give the tooling the necessary access.  This
will be read-only in nature and restricted to these specific privileges:

``SELECT,RELOAD,LOCK TABLES,SHOW VIEW,REPLICATION CLIENT``

Performance Impact
------------------

It's possible that there might be some performance degradation whilst taking a
backup of a database node which has a significant amount of data, especially if
the backup target device is the same as the source.

Aside from degradation incurred by way of I/O contention, the selection of
XtraBackup is an attempt at mitigating any kind of performance impact.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

Nick Jones (yankcrime)

Work Items
----------

1. Introduce a new Kolla image containing XtraBackup package plus dependencies
   such as scripts to handle triggering the backup;

2. Introduce a new Kolla-Ansible command and corresponding role to take a
   backup using a container launched from this image, saving data to a
   dedicated volume;

3. Documentation for new options and also restore process, along with examples.

Testing
=======

Tests should be added to validate that a backup has been taken successfully
with the default settings in place.  This would take the form of starting
another MariaDB container with the backup volume mounted as ``/var/lib/mysql``
and then performing some example queries to ensure expected data is returned.

Documentation Impact
====================

Kolla and Kolla-Ansible documentation will need updating to introduce the new
backup features and the various options that are available.

A dedicated and comprehensive section should be provide for restores, along
with example scenarios.

References
==========
[1] https://blueprints.launchpad.net/kolla/+spec/database-backup-recovery
[2] https://etherpad.openstack.org/p/kolla-rocky-ptg-db-backup-restore
[3] https://www.percona.com/doc/percona-xtrabackup/LATEST/index.html
