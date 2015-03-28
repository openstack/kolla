FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-dashboard \
        httpd httpd-mod-wsgi && yum clean all

ADD ./start.sh /start.sh

CMD ["/start.sh"]
