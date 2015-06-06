FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%designate-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y bind \
    && yum clean all \
    && cp -pr /var/named /opt/kolla/var-named

COPY start.sh /start.sh

CMD ["/start.sh"]
