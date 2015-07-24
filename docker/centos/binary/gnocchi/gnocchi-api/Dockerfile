FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%gnocchi-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum install -y openstack-gnocchi-api \
    openstack-gnocchi-carbonara \
    openstack-gnocchi-indexer-sqlalchemy \
    && yum clean all

COPY ./start.sh /start.sh
CMD ["/start.sh"]
