FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%cinder-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install required packages
RUN yum install -y lvm2 scsi-target-utils && yum clean all

# Add start scripts
COPY tgtd.sh volume-group-create.sh config-internal.sh config-external.sh /opt/kolla/
COPY start.sh /start.sh

CMD ["/start.sh"]
