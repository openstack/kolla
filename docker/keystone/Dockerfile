FROM rhel7
MAINTAINER jlabocki@redhat.com

# This Dockerfile installs the components of Keystone in a docker image as a proof of concept
RUN date > /root/date

#Install required packages
RUN yum install -y wget procps-ng net-tools && yum clean all
RUN yum install -y openstack-keystone openstack-utils openstack-selinux mariadb-galera-server socat && yum clean all

#Service token stuff
RUN export SERVICE_TOKEN=$(/usr/bin/openssl rand -hex 10) && /usr/bin/echo $SERVICE_TOKEN > /root/ks_admin_token && openstack-config --set /etc/keystone/keystone.conf DEFAULT admin_token $SERVICE_TOKEN && echo "export SERVICE_TOKEN=`cat /root/ks_admin_token`" > /root/ks_admin && echo "export SERVICE_ENDPOINT=\"http://127.0.0.1:35357/v2.0\"" >> /root/ks_admin

#Eventually use rabbitmq-server (externally, but who knows, this might work too some day)
#RUN yum install -y rabbitmq-server
#RUN yum install -y mariadb-galera-server

#Eventually use optimizied systemd for containers and use this to enable the service and start it
#RUN yum install systemd-container

ADD ./start /usr/bin/run

CMD ["/usr/bin/run"]
