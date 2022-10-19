===========================
Versions of used components
===========================

Kolla project images cover several distributions on multiple architectures. Not
all packages come from distribution repositories. Table below tries to provide
information about those which come from 3rdparty sources.

For each component used we list version used at branch release and provide
information about package sources.

.. note::
    When table mentions 'CentOS' it means both CentOS Stream 9 and Rocky Linux 9.

==============  ================  =============================================
 Name           Version           Package source information
==============  ================  =============================================
 Grafana        9.x                `Grafana install guide`_
 InfluxDB       1.8.x              `InfluxDB upstream repo`_
 Kibana         7.x                `Kibana install guide`_
 Logstash       7.x                `Logstash install guide`_
 MariaDB        10.6 (LTS)         `MariaDB Community downloads`_
 Galera         26.4 (LTS)         `MariaDB Community downloads`_
 Opensearch     2.3.x              `Opensearch install guide`_
 ProxySQL       2.4.x              `ProxySQL repository`_
 Rabbitmq       3.10.x             - CentOS:
                                     `Team RabbitMQ 'PackageCloud' repository`_
                                   - Debian/Ubuntu:
                                     `Team RabbitMQ 'Cloudsmith' repository`_
 Erlang         25.x               - CentOS aarch64:
                                     `Hrw's COPR`_
                                   - CentOS x86-64:
                                     `Team RabbitMQ 'PackageCloud' repository`_
                                   - Debian/Ubuntu:
                                     `Team RabbitMQ 'Modern Erlang' PPA`_
 TD Agent       4.4.x              `TreasureData install guide`_
 Telegraf       1.24.x             `InfluxDB upstream repo`_
==============  ================  =============================================

.. _`InfluxDB upstream repo`: https://repos.influxdata.com/
.. _`Opensearch install guide`: https://opensearch.org/downloads.html
.. _`Kibana install guide`: https://www.elastic.co/guide/en/kibana/7.10/install.html
.. _`Logstash install guide`: https://www.elastic.co/guide/en/logstash/7.9/installing-logstash.html
.. _`TreasureData install guide`: https://www.fluentd.org/download
.. _`ProxySQL repository`: https://repo.proxysql.com/ProxySQL/proxysql-2.4.x/

.. _`Team RabbitMQ 'Cloudsmith' repository`: https://www.rabbitmq.com/install-debian.html#apt-cloudsmith
.. _`Team RabbitMQ 'Modern Erlang' PPA`: https://launchpad.net/~rabbitmq/+archive/ubuntu/rabbitmq-erlang
.. _`Team RabbitMQ 'PackageCloud' repository`: https://www.rabbitmq.com/install-rpm.html#package-cloud
.. _`Hrw's COPR`: https://copr.fedorainfracloud.org/coprs/hrw/erlang-for-rabbitmq/

.. _`Grafana install guide`: https://grafana.com/grafana/download?platform=linux&edition=oss
.. _`MariaDB Community downloads`: https://mariadb.com/downloads/community/
