FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%cinder-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN pip install python-keystoneclient

COPY config-internal.sh config-external.sh /opt/kolla/
COPY ./start.sh ./check.sh /

CMD ["/start.sh"]
