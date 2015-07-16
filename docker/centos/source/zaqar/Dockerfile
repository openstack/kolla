FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./zaqar.tar /
RUN ln -s /zaqar-* /zaqar

RUN cd /zaqar \
    && useradd --user-group zaqar \
    && pip install -r requirements.txt \
    && pip install /zaqar \
    && mkdir /etc/zaqar /var/log/zaqar \
    && cp -r /zaqar/etc/* /etc/zaqar/ \
    && rm -rf /root/.cache


COPY ./start.sh /start.sh

COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
