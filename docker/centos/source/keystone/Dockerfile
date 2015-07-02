FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        httpd \
        mod_wsgi \
        && yum clean all

ADD ./keystone.tar /
RUN ln -s /keystone-* /keystone

RUN cd /keystone \
    && useradd --user-group keystone \
    && pip install -r requirements.txt \
    && pip install /keystone \
    && mkdir /etc/keystone /var/log/keystone /var/www/cgi-bin/keystone \
    && cp /keystone/etc/keystone.conf.sample /etc/keystone/keystone.conf \
    && cp -r /keystone/etc/* /etc/keystone/ \
    && cp -a httpd/wsgi-keystone.conf /etc/httpd/conf.d \
    && sed -i 's,/var/log/apache2,/var/log/httpd,' /etc/httpd/conf.d/wsgi-keystone.conf \
    && sed -i -r 's,^(Listen 80),#\1,' /etc/httpd/conf/httpd.conf \
    && cp -a httpd/keystone.py /var/www/cgi-bin/keystone/main \
    && cp -a httpd/keystone.py /var/www/cgi-bin/keystone/admin \
    && chown -R keystone: /var/www/cgi-bin/keystone /var/log/keystone \
    && chmod 755 /var/www/cgi-bin/keystone/*

COPY start.sh check.sh /
COPY config-internal.sh config-external.sh /opt/kolla/

CMD ["/start.sh"]
