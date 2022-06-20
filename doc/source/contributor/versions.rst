===========================
Versions of used components
===========================

Kolla project images cover several distributions on multiple architectures. Not
all packages come from distribution repositories. Table below tries to provide
information about those which come from 3rdparty sources.

==============  ================  =============================================
 Name           Minimal Version    Package source information
==============  ================  =============================================
 Elasticsearch  7.10               `Elasticsearch install guide`_
 Logstash       7.9                `Logstash install guide`_
 Kibana         7.10               `Kibana install guide`_
 InfluxDB       1.8.10             `InfluxDB upstream repo`_
 Telegraf       1.23.0             `InfluxDB upstream repo`_
 TD Agent       4.3.1              `TreasureData install guide`_
 ProxySQL       2.3                `ProxySQL repository`_
 HAProxy        2.2                - CentOS: "NFV extras" distro repository
                                   - Debian: distro repository
                                   - Ubuntu 20.04: `HAProxy PPA`_
 Erlang         24.3               - CentOS aarch64:
                                     `Erlang Solutions`_
                                   - CentOS x86-64:
                                     `PackageCloud modern Erlang`_
                                   - Debian/Ubuntu:
                                     `Cloudsmith.io modern Erlang`_
 Rabbitmq       3.9.20             - CentOS:
                                     `PackageCloud modern Erlang`_
                                   - Debian/Ubuntu:
                                     `Cloudsmith.io modern Erlang`_
 Grafana        9.0                `Grafana install guide`_
 OpenVSwitch    2.15               - CentOS: "NFV extras" distro repository
                                   - Debian: "OpenStack backports" distro
                                     repository
                                   - Ubuntu: Ubuntu Cloud Archive repository
 QEMU           6.2                - CentOS: distro repository
                                   - Debian: 'backports' distro repository
                                   - Ubuntu 22.04: distro repository
 libvirt        8.0                - CentOS: distro repository
                                   - Debian: 'backports' distro repository
                                   - Ubuntu 22.04: distro repository
 MariaDB        10.6 (LTS)         `MariaDB Community downloads`_
==============  ================  =============================================

.. _`InfluxDB upstream repo`: https://repos.influxdata.com/
.. _`Elasticsearch install guide`: https://www.elastic.co/guide/en/elasticsearch/reference/7.10/install-elasticsearch.html
.. _`Kibana install guide`: https://www.elastic.co/guide/en/kibana/7.10/install.html
.. _`Logstash install guide`: https://www.elastic.co/guide/en/logstash/7.9/installing-logstash.html
.. _`TreasureData install guide`: https://www.fluentd.org/download
.. _`ProxySQL repository`: https://repo.proxysql.com/ProxySQL/proxysql-2.3.x/

.. _`HAProxy PPA`: https://launchpad.net/~vbernat/+archive/ubuntu/haproxy-2.2
.. _`Cloudsmith.io modern Erlang`: https://www.rabbitmq.com/install-debian.html#apt-cloudsmith
.. _`PackageCloud modern Erlang`: https://www.rabbitmq.com/install-rpm.html#package-cloud
.. _`Erlang Solutions`: https://packages.erlang-solutions.com/rpm/centos/

.. _`Grafana install guide`: https://grafana.com/grafana/download?platform=linux&edition=oss
.. _`MariaDB Community downloads`: https://mariadb.com/downloads/community/
