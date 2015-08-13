FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./murano.tar /
RUN ln -s /murano-* /murano

RUN cd /murano \
    && pip install -r requirements.txt \
    && pip install /murano \
    && mkdir /etc/murano \
    && cd /murano \
    && tox -e genconfig \
    && cp -r etc/murano/* /etc/murano/ \
    && cp etc/murano/murano.conf.sample /etc/murano/murano.conf \
    && rm -rf /root/.cache
