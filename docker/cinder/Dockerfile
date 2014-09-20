FROM fedora-rdo-base
MAINTAINER rhallise@redhat.com

RUN yum -y install openstack-cinder && yum clean all

ADD ./start.sh /start.sh
CMD ["/start.sh"]

