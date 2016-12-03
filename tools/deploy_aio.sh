#!/bin/bash

set -o xtrace
set -o errexit

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

export KOLLA_BASE=$1
export KOLLA_TYPE=$2
export KOLLA_ANSIBLE_DIR=$(mktemp -d)

cat > /tmp/clonemap <<EOF
clonemap:
 - name: openstack/kolla-ansible
   dest: ${KOLLA_ANSIBLE_DIR}
EOF

/usr/zuul-env/bin/zuul-cloner -m /tmp/clonemap --workspace "$(pwd)" \
    --cache-dir /opt/git git://git.openstack.org \
    openstack/kolla-ansible

pushd "${KOLLA_ANSIBLE_DIR}"
# Copy configs
sudo cp -a etc/kolla /etc/
# Generate passwords
sudo tools/generate_passwords.py
./tools/deploy_aio.sh "$KOLLA_BASE" "$KOLLA_TYPE"
popd
