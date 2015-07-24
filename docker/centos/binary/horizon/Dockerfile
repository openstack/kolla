FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    openstack-dashboard \
    httpd \
    mod_wsgi \
    patch \
    && yum clean all \
    && chown -R apache:apache /usr/share/openstack-dashboard/static

# The chown is required because of this packaging bug:
# https://bugzilla.redhat.com/show_bug.cgi?id=1219006

COPY config-internal.sh config-external.sh horizon-bug-1469284.patch /opt/kolla/
# TODO(mduggan): Need to remove this patch once a fix for
# https://bugs.launchpad.net/kolla/+bug/1469284 becomes available upstream.
# Review for this bug is at https://review.openstack.org/#/c/167981/
RUN patch /usr/lib/python2.7/site-packages/openstack_auth/user.py < /opt/kolla/horizon-bug-1469284.patch
COPY ./start.sh /start.sh

CMD ["/start.sh"]
