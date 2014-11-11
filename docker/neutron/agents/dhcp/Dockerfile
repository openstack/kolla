FROM kollaglue/fedora-rdo-neutron-base:l3_ovs_wip
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install required packages
RUN yum install -y openstack-neutron \
        yum clean all;

# Add required scripts
ADD ./start.sh /start.sh
ADD ./check.sh /check.sh
ADD ./sudoers.sh /sudoers.sh

# Configure and run the service
CMD ["/start.sh"]
