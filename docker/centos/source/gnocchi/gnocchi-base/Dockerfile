FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./gnocchi.tar /
RUN ln -s /gnocchi-* /gnocchi

RUN cd /gnocchi \
    && useradd --user-group gnocchi \
    && pip install -r requirements.txt \
    && pip install /gnocchi \
    && mkdir /etc/gnocchi /var/log/gnocchi \
    && cp -r /gnocchi/etc/* /etc/gnocchi/ \
    && rm -rf /root/.cache
