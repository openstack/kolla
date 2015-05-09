FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%nova-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

RUN yum -y install \
    novnc openstack-nova-novncproxy && \
    yum clean all

RUN rpm -e --nodeps python-websockify

RUN yum -y install https://kojipkgs.fedoraproject.org//packages/python-websockify/0.5.1/1.el7/noarch/python-websockify-0.5.1-1.el7.noarch.rpm

ADD start.sh /start.sh

CMD ["/start.sh"]
