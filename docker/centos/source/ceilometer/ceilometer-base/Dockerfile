FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./ceilometer.tar /
RUN ln -s /ceilometer-* /ceilometer

RUN cd /ceilometer \
    && useradd --user-group ceilometer \
    && pip install -r requirements.txt \
    && pip install /ceilometer \
    && mkdir /etc/ceilometer /var/log/ceilometer \
    && cp -r /ceilometer/etc/* /etc/ \
    && rm -rf /root/.cache

CMD ["/start.sh"]
