FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./cinder.tar /
RUN ln -s /cinder-* /cinder

RUN cd /cinder \
    && useradd --user-group cinder \
    && pip install -r requirements.txt \
    && pip install /cinder \
    && tox -egenconfig \
    && mkdir /etc/cinder /var/log/cinder \
    && cp -r /cinder/etc/cinder/* /etc/cinder/ \
    && cp /etc/cinder/cinder.conf.sample /etc/cinder/cinder.conf \
    && chown -R cinder: /etc/cinder /var/log/cinder \
    && rm -rf /root/.cache
