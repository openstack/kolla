FROM kollaglue/fedora-rdo-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install rabbitmq-server; yum clean all
ADD rabbitmq.config /etc/rabbitmq/
ADD rabbitmq-env.conf /etc/rabbitmq/
ADD start.sh /start.sh
CMD ["/start.sh"]
