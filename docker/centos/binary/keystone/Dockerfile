FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

#Install required packages
RUN yum -y install openstack-keystone \
        python-keystoneclient \
        && yum clean all

# Add start-up and check scripts
ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

# Run the Keystone start script
CMD ["/start.sh"]
