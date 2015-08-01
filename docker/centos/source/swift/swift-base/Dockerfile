FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./swift.tar /
RUN ln -s /swift-* /swift

RUN cd /swift \
    && useradd --user-group swift \
    && pip install -r requirements.txt \
    && pip install /swift \
    && mkdir /etc/swift /var/log/swift \
    && cp -r /swift/etc/* /etc/swift/ \
    && rm -rf /root/.cache

COPY config-swift.sh build-swift-ring.py /opt/kolla/

RUN mkdir /opt/swift

CMD ["/start.sh"]
