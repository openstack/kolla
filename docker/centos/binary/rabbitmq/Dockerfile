FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
   hostname \
   rabbitmq-server && \
   yum clean all && \
   /usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management

COPY rabbitmq.config rabbitmq-env.conf /etc/rabbitmq/
COPY config-rabbit.sh config-external.sh config-internal.sh /opt/kolla/
COPY start.sh /start.sh

CMD ["/start.sh"]
