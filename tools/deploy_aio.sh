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
export RAW_INVENTORY=/tmp/kolla/raw_inventory

sudo ansible-playbook -i ${RAW_INVENTORY} --become tests/ansible_generate_inventory.yml
sudo ansible-playbook -i ${RAW_INVENTORY} --become -e type=$KOLLA_TYPE -e base=$KOLLA_BASE tests/ansible_generate_config.yml > /tmp/logs/ansible/generate_config
sudo ip l a fake_interface type dummy

sudo tools/generate_passwords.py
sudo chmod -R 777 /etc/kolla
sudo tools/kolla-ansible -i ${RAW_INVENTORY} -vvv prechecks > /tmp/logs/ansible/prechecks1
sudo tools/kolla-ansible -i ${RAW_INVENTORY} -vvv deploy > /tmp/logs/ansible/deploy
sudo tools/kolla-ansible -i ${RAW_INVENTORY} -vvv post-deploy > /tmp/logs/ansible/post-deploy

popd
