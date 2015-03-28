FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%neutron-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

#Install required packages
RUN yum install -y openstack-neutron \
        python-neutronclient \
        mariadb \
        && yum clean all

VOLUME /var/lib/neutron

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
