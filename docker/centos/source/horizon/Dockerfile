FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./horizon.tar /
RUN ln -s /horizon-* /horizon

RUN yum install -y \
    httpd \
    mod_wsgi \
  && yum clean all

RUN cd /horizon \
    && useradd --user-group horizon \
    && pip install -r requirements.txt \
    && pip install /horizon \
    && mkdir -p \
        /etc/openstack-dashboard \
        /usr/share/openstack-dashboard/static \
        /var/log/horizon \
    && cp -r /horizon/openstack_dashboard /usr/share/openstack-dashboard/ \
    && cp /horizon/openstack_dashboard/local/local_settings.py.example \
        /etc/openstack-dashboard/local_settings \
    && ln -s /etc/openstack-dashboard/local_settings \
        /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py \
    && cp /horizon/manage.py /usr/share/openstack-dashboard \
    && python /usr/share/openstack-dashboard/manage.py collectstatic --noinput \
    && chown -R apache:apache /usr/share/openstack-dashboard/static \
    && rm -rf /root/.cache

# The chown is required because of this packaging bug:
# https://bugzilla.redhat.com/show_bug.cgi?id=1219006

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
