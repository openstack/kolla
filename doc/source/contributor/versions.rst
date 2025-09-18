===========================
Versions of used components
===========================

Kolla project images cover several distributions on multiple architectures. Not
all packages come from distribution repositories. Table below tries to provide
information about those which come from 3rdparty sources.

For each component used we list version used at branch release and provide
information about package sources.

.. note::
    When table mentions 'CentOS' it means both CentOS Stream 10 and Rocky Linux 10.

==============  ================  =============================================
 Name           Version           Package source information
==============  ================  =============================================
 Grafana        9.x                `Grafana install guide`_
 InfluxDB       1.8.x              `InfluxDB upstream repo`_
 Kibana         7.x                `Kibana install guide`_
 Logstash       7.x                `Logstash install guide`_
 MariaDB        10.11 (LTS)        `MariaDB Community downloads`_
 Galera         26.4 (LTS)         `MariaDB Community downloads`_
 OpenSearch     3.x                `OpenSearch install guide`_
 ProxySQL       2.7.x              `ProxySQL repository`_
 Rabbitmq       4.1.x              - CentOS/Rocky:
                                     `Team RabbitMQ 'Cloudsmith' repo (RPM)`_
                                   - Debian/Ubuntu:
                                     `Team RabbitMQ 'Cloudsmith' repo (Deb)`_
 Erlang         27.X               - CentOS/Rocky aarch64:
                                     `openstack-kolla COPR`_
                                   - CentOS/Rocky x86-64:
                                     `Team RabbitMQ 'Cloudsmith' repo (RPM)`_
                                   - Debian/Ubuntu:
                                     `Team RabbitMQ 'Modern Erlang' PPA`_
 Fluentd        6.x (LTS)          `Fluentd install guide`_
 Telegraf       1.24.x             `InfluxDB upstream repo`_
==============  ================  =============================================

.. _`InfluxDB upstream repo`: https://repos.influxdata.com/
.. _`OpenSearch install guide`: https://opensearch.org/downloads.html
.. _`Kibana install guide`: https://www.elastic.co/guide/en/kibana/7.10/install.html
.. _`Logstash install guide`: https://www.elastic.co/guide/en/logstash/7.9/installing-logstash.html
.. _`Fluentd install guide`: https://www.fluentd.org/download
.. _`ProxySQL repository`: https://repo.proxysql.com/ProxySQL/proxysql-3.0.x/

.. _`Team RabbitMQ 'Cloudsmith' repo (Deb)`: https://www.rabbitmq.com/install-debian.html#apt-cloudsmith
.. _`Team RabbitMQ 'Modern Erlang' PPA`: https://launchpad.net/~rabbitmq/+archive/ubuntu/rabbitmq-erlang
.. _`Team RabbitMQ 'Cloudsmith' repo (RPM)`: https://www.rabbitmq.com/docs/install-rpm#cloudsmith
.. _`openstack-kolla COPR`: https://copr.fedorainfracloud.org/coprs/g/openstack-kolla/rabbitmq-erlang-27/

.. _`Grafana install guide`: https://grafana.com/grafana/download?platform=linux&edition=oss
.. _`MariaDB Community downloads`: https://mariadb.com/downloads/community/
