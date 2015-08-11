FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./glance.tar /
RUN ln -s /glance-* /glance

RUN cd /glance \
    && useradd --user-group glance \
    && pip install -r requirements.txt \
    && pip install /glance \
    && mkdir /etc/glance /var/log/glance \
    && cp -r /glance/etc/*  /etc/glance/ \
    && rm -rf /root/.cache

CMD ["/start.sh"]
