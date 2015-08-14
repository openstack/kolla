FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./heat.tar /
RUN ln -s /heat-* /heat

RUN cd /heat \
    && useradd --user-group heat \
    && pip install -r requirements.txt \
    && pip install /heat \
    && mkdir /etc/heat /var/log/heat \
    && cp -r /heat/etc/heat/* /etc/heat/ \
    && rm -rf /root/.cache
