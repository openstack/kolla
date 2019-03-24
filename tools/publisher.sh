# Script which is run in dockerhub publisher pipeline
# It will organize build/deploy gates and then publish images to final place

export ZUUL_REF=$ZUUL_REF
export BRANCH=$(echo "$ZUUL_BRANCH" | cut -d/ -f2)
export TMP_REGISTRY="opt/"
export PUBLISHER=1
export SIGNOFF_FILENAME=${BASE_DISTRO}-${INSTALL_TYPE}-registry-${BRANCH}.txt
export FILENAME=${BASE_DISTRO}-${INSTALL_TYPE}-registry-${BRANCH}.tar.gz

# Ansible deployment gate to test out images
function deploy_ansible {
    export KOLLA_ANSIBLE_DIR=$(mktemp -d)
    cat > /tmp/clonemap <<EOF
clonemap:
 - name: openstack/kolla-ansible
   dest: ${KOLLA_ANSIBLE_DIR}
EOF

    /usr/zuul-env/bin/zuul-cloner -m /tmp/clonemap --workspace "$(pwd)" \
        --cache-dir /opt/git https://git.openstack.org openstack/kolla-ansible

    pushd "${KOLLA_ANSIBLE_DIR}"
        tools/setup_gate.sh
    popd
}

# If test passes, add link to test data which later will be added to image
function signoff {
    mkdir -p images/
    curl -o images/$SIGNOFF_FILENAME http://tarballs.openstack.org/kolla/images/tmp/$SIGNOFF_FILENAME
    echo http://logs.openstack.org/$LOG_PATH >> images/$SIGNOFF_FILENAME
}

# Building images that are supposed to be tested later
if [[ $ACTION == "build" ]]; then
    tools/gate_run.sh
    sudo touch images/$SIGNOFF_FILENAME
    sudo chmod 777 images/$SIGNOFF_FILENAME

    echo http://logs.openstack.org/$LOG_PATH >> images/$SIGNOFF_FILENAME
    exit 0
fi
if [[ $ACTION == "deploy-multinode" ]]; then
    if [[ $ORCH_ENGINE == "ansible" ]]; then
        deploy_ansible
        signoff
        exit 0
    fi
fi

# After all tests pass, move images from temp to final dir on tarballs.o.o
if [[ $ACTION == "save" ]]; then
    mkdir -p images/
    wget -q -c -O "/tmp/$FILENAME" \
        "http://tarballs.openstack.org/kolla/images/tmp/$FILENAME"
    curl -o /tmp/$SIGNOFF_FILENAME http://tarballs.openstack.org/kolla/images/tmp/$SIGNOFF_FILENAME
    gunzip /tmp/$FILENAME
    tar -rf /tmp/${BASE_DISTRO}-${INSTALL_TYPE}-registry-${BRANCH}.tar /tmp/$SIGNOFF_FILENAME
    gzip /tmp/${BASE_DISTRO}-${INSTALL_TYPE}-registry-${BRANCH}.tar
    ls -la /tmp/
    sudo mv /tmp/$FILENAME images/publisher-$FILENAME
fi

