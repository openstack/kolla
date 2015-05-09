FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-dashboard \
    httpd \
    httpd-mod-wsgi \
    && yum clean all \
    && chown -R apache:apache /usr/share/openstack-dashboard/static

# The chown is required because of this packaging bug:
# https://bugzilla.redhat.com/show_bug.cgi?id=1219006

ADD ./start.sh /start.sh

CMD ["/start.sh"]
