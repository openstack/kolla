FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./barbican.tar /
RUN ln -s /barbican-* /barbican

RUN cd /barbican \
    && useradd --user-group barbican \
    && pip install uwsgi \
    && pip install -r requirements.txt \
    && pip install /barbican \
    && mkdir /etc/barbican /var/log/barbican \
    && cp -r /barbican/etc/* /etc/barbican/ \
    && rm -rf /root/.cache

COPY ./start.sh /start.sh
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
