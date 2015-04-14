FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%cinder-base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

# Install required packages
# https://bugs.launchpad.net/kolla/+bug/1460129
# Iscsi will be removed from cinder-volume in a later patch
# so that we continue to follow the container best practices.
# There will also be other backends for cinder and iscsi should
# not be hardcoded here.
RUN yum install -y lvm2 scsi-target-utils && yum clean all

# Add start scripts
COPY start.sh /start.sh
COPY volume-group-create.sh /opt/kolla/volume-group-create.sh

# Start supervisor
CMD ["/start.sh"]
