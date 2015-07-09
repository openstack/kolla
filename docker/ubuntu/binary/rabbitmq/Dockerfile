FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN apt-get install -y --no-install-recommends \
        hostname \
        rabbitmq-server \
    && apt-get clean \
    && /usr/lib/rabbitmq/bin/rabbitmq-plugins --offline enable rabbitmq_management

COPY rabbitmq.config rabbitmq-env.conf /etc/rabbitmq/
COPY config-rabbit.sh config-external.sh config-internal.sh /opt/kolla/
COPY start.sh /start.sh

CMD ["/start.sh"]
