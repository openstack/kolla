FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

ADD ./cinder.tar /
RUN ln -s /cinder-* /cinder

RUN yum -y install lvm2 \
    && yum clean all \
    && cd /cinder \
    && useradd --user-group cinder \
    && pip install -r requirements.txt \
    && pip install /cinder \
    && mkdir /etc/cinder /var/log/cinder \
    && cp -r /cinder/etc/cinder/* /etc/cinder/ \
    && chown -R cinder: /etc/cinder /var/log/cinder \
    && rm -rf /root/.cache \
    && sed -i "s|udev_rules = 1|udev_rules = 0|g" /etc/lvm/lvm.conf \
    && sed -i "s|udev_sync = 1|udev_sync = 0|g" /etc/lvm/lvm.conf

# NOTE(sdake): The sed operations make LVM tools work inside a container - see
# https://groups.google.com/forum/#!topic/docker-user/n4Xtvsb4RAw
