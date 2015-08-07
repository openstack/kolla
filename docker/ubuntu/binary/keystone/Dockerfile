FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN apt-get install -y --no-install-recommends \
        apache2 \
        keystone \
        libapache2-mod-wsgi \
        python-keystoneclient \
    && apt-get clean

RUN curl -o /etc/apache2/sites-available/wsgi-keystone.conf \
    https://raw.githubusercontent.com/openstack/keystone/stable/kilo/httpd/wsgi-keystone.conf
RUN ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled
RUN mkdir -p /var/www/cgi-bin/keystone
RUN cp -a /usr/share/keystone/wsgi.py /var/www/cgi-bin/keystone/main
RUN cp -a /usr/share/keystone/wsgi.py /var/www/cgi-bin/keystone/admin
RUN chown -R keystone:keystone /var/www/cgi-bin/keystone
RUN chmod 755 /var/www/cgi-bin/keystone/*

COPY start.sh /

CMD ["/start.sh"]
