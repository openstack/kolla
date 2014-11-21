FROM kollaglue/fedora-rdo-base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN curl -O https://repos.fedorapeople.org/repos/openstack/openstack-juno/fedora-21/openstack-zaqar-2014.2-1.fc22.noarch.rpm
RUN curl -O https://repos.fedorapeople.org/repos/openstack/openstack-juno/fedora-21/python-oslo-utils-0.3.0-1.fc22.noarch.rpm
RUN curl -O https://repos.fedorapeople.org/repos/openstack/openstack-juno/fedora-21/python-keystonemiddleware-1.2.0-1.fc22.noarch.rpm
RUN yum -y localinstall python-oslo-utils-0.3.0-1.fc22.noarch.rpm \
           python-keystonemiddleware-1.2.0-1.fc22.noarch.rpm \
           openstack-zaqar-2014.2-1.fc22.noarch.rpm \
           ; yum clean all

EXPOSE 8888

ADD ./start.sh /start.sh
ADD ./check.sh /check.sh

CMD ["/start.sh"]
