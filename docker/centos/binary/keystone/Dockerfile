FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install openstack-keystone \
        python-keystoneclient \
        httpd \
        mod_wsgi \
        && yum clean all

RUN mkdir -p /var/www/cgi-bin/keystone
RUN cp -a /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d
RUN sed -i 's,/var/log/apache2,/var/log/httpd,' /etc/httpd/conf.d/wsgi-keystone.conf
RUN sed -i -r 's,^(Listen 80),#\1,' /etc/httpd/conf/httpd.conf
RUN cp -a /usr/share/keystone/keystone.wsgi /var/www/cgi-bin/keystone/main
RUN cp -a /usr/share/keystone/keystone.wsgi /var/www/cgi-bin/keystone/admin
RUN chown -R keystone:keystone /var/www/cgi-bin/keystone
RUN chmod 755 /var/www/cgi-bin/keystone/*

# Add start-up and check scripts
COPY ./start.sh /start.sh
COPY ./check.sh /check.sh

# Run the Keystone start script
CMD ["/start.sh"]
