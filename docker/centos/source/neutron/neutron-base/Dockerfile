FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./neutron.tar /
RUN ln -s /neutron-* /neutron

RUN cd /neutron \
    && useradd --user-group neutron \
    && pip install -r requirements.txt \
    && pip install /neutron \
    && mkdir /etc/neutron /usr/share/neutron /var/log/neutron \
    && cp -r etc/* /etc/neutron/ \
    && cp -r etc/neutron/* /etc/neutron/ \
    && cp etc/api-paste.ini /usr/share/neutron \
    && mv /etc/neutron/neutron/ /etc/neutron/plugins/ \
    && chown -R neutron: /etc/neutron /var/log/neutron \
    && rm -rf /root/.cache

COPY config-sudoers.sh /opt/kolla/
