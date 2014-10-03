FROM kollaglue/fedora-rdo-base
MAINTAINER Lars Kellogg-Stedman <lars@redhat.com>

RUN yum -y install rabbitmq-server; yum clean all
ADD rabbitmq.config /etc/rabbitmq/
ADD rabbitmq-env.conf /etc/rabbitmq/
ADD init-rabbitmq.sh /start.sh
CMD ["/start.sh"]
