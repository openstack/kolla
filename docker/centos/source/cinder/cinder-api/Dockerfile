FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%cinder-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN pip install python-keystoneclient

COPY start.sh /
COPY config-external.sh /opt/kolla/

CMD ["/start.sh"]
