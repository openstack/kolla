FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install required packages
RUN yum -y install rabbitmq-server && yum clean all

# Run the management plugin
RUN /usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management

# Copy Rabbit conf files
ADD rabbitmq.config /etc/rabbitmq/
ADD rabbitmq-env.conf /etc/rabbitmq/

# Copy start-up script
ADD start.sh /start.sh

# Start Rabbit through the start script
CMD ["/start.sh"]
