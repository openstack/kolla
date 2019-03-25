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
    --cache-dir /opt/git https://git.openstack.org \
    openstack/kolla-ansible

pushd "${KOLLA_ANSIBLE_DIR}"

function get_logs {
    sudo ansible-playbook -i ${INVENTORY} --become ${KOLLA_ANSIBLE_DIR}/tests/ansible_get_logs.yml > /tmp/logs/ansible/get-logs
}

# Copy configs
sudo cp -a etc/kolla /etc/
# Generate passwords
export INVENTORY=/tmp/kolla/inventory

sudo ansible-playbook -i ${INVENTORY} --become tests/ansible_generate_inventory.yml
sudo ansible-playbook -i ${INVENTORY} --become -e action="deploy" -e type=$KOLLA_TYPE -e base=$KOLLA_BASE tests/ansible_generate_config.yml > /tmp/logs/ansible/generate_config

trap get_logs EXIT

sudo ip l a fake_interface type dummy

sudo tools/generate_passwords.py
sudo chmod -R 777 /etc/kolla
sudo tools/kolla-ansible -i ${INVENTORY} -vvv prechecks > /tmp/logs/ansible/prechecks
sudo tools/kolla-ansible -i ${INVENTORY} -vvv deploy > /tmp/logs/ansible/deploy
sudo tools/kolla-ansible -i ${INVENTORY} -vvv post-deploy > /tmp/logs/ansible/post-deploy

get_logs

popd
