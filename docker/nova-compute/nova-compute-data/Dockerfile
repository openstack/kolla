FROM %%KOLLA_NAMESPACE%%/%%KOLLA_PREFIX%%base:%%KOLLA_TAG%%
MAINTAINER Kolla Project (https://launchpad.net/kolla)

VOLUME [ "/var/lib/nova" ]
VOLUME [ "/var/lib/libvirt" ]
VOLUME [ "/etc/libvirt/qemu" ]

# Command needed to start the data container.
# Note: data containers do not need to be persistent.
CMD ["/bin/true"]
