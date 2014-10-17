FROM kollaglue/fedora-rdo-neutron-base
MAINTAINER Daneyon Hansen <danehans@cisco.com>

#Install required packages
RUN yum install -y openstack-neutron \
        python-neutronclient \
        mariadb \
        ; yum clean all

VOLUME /var/lib/neutron

EXPOSE 9696

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
