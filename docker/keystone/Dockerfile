FROM rhel7
MAINTAINER jlabocki@redhat.com

#Install required packages
RUN yum install -y wget procps-ng net-tools && yum clean all
RUN yum install -y openstack-keystone openstack-utils openstack-selinux && yum clean all

ADD ./start.sh /start.sh

CMD ["/start.sh"]
