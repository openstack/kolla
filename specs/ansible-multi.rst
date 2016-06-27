..
   This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================
Multi-node Ansible
==================

This blueprint specifies an approach to automate the deployment of OpenStack
using Ansible and Docker best practices.  The overriding principles used in
this specification are simplicity, flexibility and optimized deployment speed.

Problem description
===================

Kolla can be deployed multi-node currently.  To do so, the environment
variables must be hand edited to define the hosts to connect to for various
services.

To implement HA in our containers, we need multi-node deployment operational
so we can validate the high availability implementation.

To meet our community approved mission, we must implement a deployment tool
and Ansible provides the most efficient development path while ensuring ease
of use.

Use cases
---------

1. Deploy Kolla's Docker containers multi-node and generate a one-hundred node
   working OpenStack deployment out of the box with minimal Operator
   configuration.
2. Offer a fully customizable configuration enabling an unopinionated
   deployment of OpenStack.
3. Upgrade an OpenStack deployment by Operator command.
4. Offer our container content as a building block to third party downstream
   deployment tools.

Proposed change
===============

The docker-compose tool is single node and does nearly the same job as Ansible
would in this specification.  As a result, we recommend deprecating
docker-compose as the default deployment system for Kolla.

To replace it, we recommend Ansible as a technology choice.  Ansible is easy
to learn, easy to use, and offers a base set of functionality to solve
deployment as outlined in our four use cases.

We recommend three models of configuration.

The first model is based upon internally configuring the container and having
the container take responsibility for all container configuration including
database setup, database synchronization, and keystone registration.  This
model uses docker-compose and docker as dependencies.  Existing containers will
be maintained but new container content will use either of the two remaining
models.  James Slagle (TripleO PTL on behalf of our downstream TripleO
community) was very clear that he would prefer to see this model stay available
and maintained.  As TripleO enters the world of Big Tent, they don't intend to
deploy all of the services, and as such it doesn't make sense to maintain this
legacy operational mode for new container content except on demand of our
downstreams, hopefully with their assistance.  This model is called
CONFIG_INSIDE.

The second model and third model configure the containers outside of the
container.  These models depend on Ansible and Docker.  In the future, the
OpenStack Puppet, OpenStack Chef and TripleO communities may decide to switch
to one of these two models in which case these communities may maintain tooling
to integrate with Kolla.  The major difference between these two models is that
one offers immutability and single source of truth (CONFIG_OUTSIDE_COPY_ONCE),
while the third model trades these two properties to allow an Operator to
directly modify configuration files on a system and have the configuration be
live in the container (CONFIG_OUTSIDE_COPY_ALWAYS).  Because
CONFIG_OUTSIDE_COPY_ALWAYS requires direct Operator intervention on a node, and
we prefer as a community Operators interact with the tools provided by Kolla,
CONFIG_OUTSIDE_COPY_ONCE will be the default.

We do not have to further enhance two sets of container configuration, but
instead can focus our development effort on the default Ansible configuration
methods.  If a defect is found in one of the containers based upon the
CONFIG_INSIDE model, the community will repair it.

Finally we will implement a complete Ansible deployment system.  The details
of the implementation are covered in a later section in this specification.
We estimate this will be approximately ~1000 LOC defining ~100 Ansible tasks.
We further estimate the total code base when complete will be under 6 KLOC.

The CONFIG_INSIDE model of configuration maintains the immutable,
declarative, and idempotent nature of the Kolla containers, as defined by our
current Kolla best practices but is opinionated in configuration.

The CONFIG_OUTSIDE_COPY_ONCE model of configuration maintains the immutable and
declarative nature of the Kolla containers, as defined by our current Kolla
best practices while introducing completely customizable configuration.

The CONFIG_OUTSIDE_COPY_ALWAYS model of configuration offers the Operator
greater flexibility in managing their deployment, at greater risk of damaging
their deployment.  It trades one set of best practices for another,
specifically the Kolla container best practices for flexibility.

Security impact
---------------

None.

Performance Impact
------------------

Multi-node deployment speed will be rapidly improved.

Implementation
==============

The following section uses the Keystone container as an example.

On container start, a simple shell script will be run.

Passed into the container will be the CONFIG_STRATEGY environment variable with
the following options:

    CONFIG_STRATEGY="CONFIG_INSIDE"
    CONFIG_STRATEGY="CONFIG_OUTSIDE_COPY_ALWAYS"
    CONFIG_STRATEGY="CONFIG_OUTSIDE_COPY_ONCE"

CONFIG_INSIDE will match the current crudini.sh implementation.

The shell script will be similar in nature to the following:

    case $CONFIG_STRATEGY in
        CONFIG_INSIDE)
            # We exec on crudini.sh to keep the same behaviour as current
            exec /crudini.sh
            ;;
        CONFIG_OUTSIDE_COPY_ONCE|CONFIG_OUTSIDE_COPY_ALWAYS)
            # We source this file to allow variables to be set if needed
            source /config_outside.sh
            ;;
        *)
            echo '$CONFIG_STRATEGY is not set properly'
            exit 1
            ;;
    esac

    exec $CONFIG_STRATEGY_BINARY_NAME

The crudini.sh script would be almost identical to the existing start.sh script
while the config_outside.sh would copy the files to the appropriate location
and set the proper permissions on those files. The $CONFIG_STRATEGY variable
would be checked to see if the files should be copied or it should exit early.

The following bindmounts would be applied to the container in the above example
for different CONFIG_STRATEGY values:

    CONFIG_INSIDE - no bind mount
    CONFIG_OUTSIDE_COPY_ONCE - {{ HOST_CONFIG_DIR }}/keystone:/opt/kolla/configs/keystone:ro
    CONFIG_OUTSIDE_COPY_ALWAYS - {{ HOST_CONFIG_DIR }}/keystone:/opt/kolla/configs/keystone:ro

{{ HOST_CONFIG_DIR }} would be an Ansible variable with the default of
/opt/kolla/configs. This same pattern will be used for most containers, unless
there is a compelling technical reason not to do so.

An Ansible role represents a service in OpenStack.  The Ansible role contains
3 major sections.  This same pattern will be used for all supported
OpenStack containers.

Each Ansible role has a set of default key/value pairs.  An example key/value
file for Keystone is:

    ---
    container: "keystone"
    database_password: "{{ database_keystone_password }}"


The second major section of a Ansible role are the role tasks.  The seven
tasks we will implement per role (i.e. OpenStack Service):

 * bootstrap - database initialization and add roles to keystone
 * pull - pulls the latest container from the registry
 * main - Does the main job of orchestrating the role
 * config - Joins the default configuration and the user augmented
   configuration and saves the resulting file to be bind-mounted
 * start - Similar in nature to a docker compose YAML file - defines the
   defaults for the container start operation.
 * stop - Stops the container
 * upgrade - Upgrades to the latest container content

The details of how these role tasks operate is an implementation detail.

Finally each Ansible role has a default template.  An example of a default
template for Keystone is:

    [DEFAULT]
    verbose = {{ keystone_verbose }}
    debug = {{ keystone_debug }}

    bind_host = {{ ansible_br_mgmt['ipv4']['address'] }}

    admin_token = {{ keystone_admin_token }}

    public_endpoint = http://{{ keystone_service_ip }}:{{ keystone_service_public_port }}
    admin_endpoint = http://{{ keystone_service_ip }}:{{ keystone_service_admin_port }}

    log_file = {{ keystone_log_file }}
    log_dir = {{ keystone_log_dir }}

    [database]
    connection = mysql://{{ keystone_db_user }}:{{ database_keystone_password }}@{{ keystone_service_ip }}/keystone

    [revoke]
    driver = keystone.contrib.revoke.backends.sql.Revoke

This role default will contain sufficient mandatory configuration options to
create a working deployment.  If the Operator wishes to augment the Keystone
configuration, an augmentation file can be added to the deployment.  An example
augmentation file in /etc/kolla/keystone.aug is:

    [DEFAULT]
    public_endpoint = https://{{ keystone_service_ip }}:{{ keystone_service_public_port }}

    [ipman]
    life = "Two Words. Horizontal. Vertical. Make a mistake - Horizontal.  Stay standing and you win."

This augmentation file will keep the original default configurations but
replace public_endpoint with an https endpoint instead of an http endpoint.
Further the [ipman] section will be added to the file placed by Ansible in
the target host's configuration directory.

The end result of the merge will be a single file on the host that is in the
appropriate format for the OpenStack service to consume containing the content
of both the Ansible default file and the augmentation file.

The final implication of these Ansible best practices is that an Operator can
deploy in 1 hour or less a one-hundred node OpenStack deployment out of the
box using Kolla containers with Ansible deployment tooling with minimal
configuration.  If additional customization is required for the Operator's
environment, this can be achieved via augmentation files developed by the
Operator.

NB: to override any default key/value pair (the key is located in {{ }} above
and replaced by the value by Ansible), there is one global override file to
configure the deployment called /etc/kolla/globals.yml

We will implement a simple shell script called kolla-ansible which wraps
ansible-playbook.  It will implement four commands which operate on the
OpenStack deployment globally.  It will automatically load the globals.yml
overrides and an inventory file located in /etc/kolla executing the appropriate
roles for all of the deployed containers.  The initial supported
commands are:

1. kolla-ansible deploy
2. kolla-ansible start
3. kolla-ansible stop
4. kolla-ansible upgrade

Ansible supports a model of deployment using an inventory file.  The inventory
file specifies which nodes get assigned which roles.  For an example of an
inventory file, see:

    https://github.com/SamYaple/yaodu/blob/master/ansible/inventories/production

To the untrained eye, this looks like a bunch of heavy wizardy.  I personally
believe we will in some way merge our globals.yml and the inventory file into
one master configuration file and generate the globals.yml and Ansible-specific
inventory file on each kolla-ansible operation.  The long term goal is to get
to one configuration file with "all the things" needed to deploy OpenStack.
This would permit a GUI to simply configure the deployment.

How this is done or if it is done remains an implementation detail which may
warrant expanding this specification or a completely new specification in the
future.  As we obtain more experience with what we are developing, we will
have a more complete picture of what this master configuration file format will be.

The implementation described in this section is just a sample of the
implementation details required.  We intend to refactor Sam Yaple's fantastic
vision with yaodu (https://github.com/SamYaple/yaodu/) into Kolla to
implement Ansible deployment of OpenStack while retaining Kolla, Docker, and
Ansible best practices and conventions.

Assignee(s)
-----------

Primary assignees:

diga
fangfenghua
harmw
samyaple
sdake

The kolla core team will support and execute this specification through normal
workflow operations.

Work Items
----------

1. Convert all fat containers to thin containers to facilitate this work.
2. Move all start.sh scripts to crudini.sh and create the function to execute
   the configuration strategy across containers.
3. Rename the kolla script to kolla-compose and create a new kolla-ansible
   script to manage playbook operation.
4. Refactor the remaining portions of yaodu that are compatible with Kolla into
   the Kolla code base.
5. Implement our existing crudini defaults in Ansible.

Testing
=======

Functional tests will be implemented in the OpenStack check/gating system to
automatically check that the Ansible deployment works for an AIO environment.

Documentation Impact
====================

The developer quickstart must be augmented with instructions to use the new
Ansible deployment methodology.
