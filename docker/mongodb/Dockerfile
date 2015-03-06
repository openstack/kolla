FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install mongodb mongodb-server; yum clean all

RUN mkdir -p /data/db

VOLUME /data/db
VOLUME /var/log/mongodb

EXPOSE 27017

ENTRYPOINT exec /bin/mongod --dbpath /data/db --logpath /var/log/mongodb/mongo.log --noprealloc --smallfiles
