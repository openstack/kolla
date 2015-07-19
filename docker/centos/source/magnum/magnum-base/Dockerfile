FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./magnum.tar /
RUN ln -s /magnum-* /magnum

RUN cd /magnum \
    && useradd --user-group magnum \
    && pip install -r requirements.txt \
    && pip install /magnum \
    && mkdir /etc/magnum /var/log/magnum \
    && cp -r /magnum/etc/* /etc/magnum/

RUN mkdir -p /opt/kolla
COPY config-magnum.sh /opt/kolla/config-magnum.sh
