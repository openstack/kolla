FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
        bridge-utils \
    && yum clean all

RUN pip install \
    python-cinderclient \
    python-keystoneclient

ADD ./nova.tar /
RUN ln -s /nova-* /nova

RUN cd /nova \
    && useradd --user-group nova \
    && pip install -r requirements.txt \
    && pip install /nova \
    && tox -egenconfig \
    && mkdir /etc/nova /var/log/nova \
    && cp /nova/etc/nova/nova.conf.sample /etc/nova/nova.conf \
    && cp -r /nova/etc/nova/* /etc/nova/ \
    && chown -R nova: /etc/nova /var/log/nova \
    && rm -rf /root/.cache

COPY config-nova.sh /opt/kolla/config-nova.sh
