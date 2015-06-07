#!/bin/bash

# This script expects the following to be installed:
# curl, libguestfs-tools-c

IMAGE_URL=http://archive.fedoraproject.org/pub/fedora/linux/releases/21/Cloud/Images/x86_64
IMAGE=Fedora-Cloud-Base-20141203-21.x86_64.qcow2
TARGET_DIR=/var/lib/libvirt/images
TARGET=fedora-21-x86_64
export LIBGUESTFS_BACKEND=direct

if ! [ -f "$IMAGE" ]; then
    echo "Downloading $IMAGE"
    curl -L -O $IMAGE_URL/$IMAGE
fi

echo "Copying $IMAGE to $TARGET"
cp "$IMAGE" $TARGET_DIR/$TARGET


TMPFILE=$(mktemp /tmp/kolla-ifcfg-eth1.XXXXXXXXXX)
cat > $TMPFILE <<EOF
DEVICE=eth1
BOOTPROTO=none
ONBOOT=yes
DEFROUTE=no
EOF


virt-customize \
    --add $TARGET_DIR/$TARGET \
    --upload $TMPFILE:/etc/sysconfig/network-scripts/ifcfg-eth1

# SELinux relabeling requires virt-customize to have networking disabled
# https://bugzilla.redhat.com/show_bug.cgi?id=1122907
virt-customize --add $TARGET_DIR/$TARGET --selinux-relabel --no-network

rm -f $TMPFILE

echo "Finished building image:"
ls -l $TARGET_DIR/$TARGET
