#!/bin/bash

set -e

: ${SOURCE_INSTALL_METHOD:=curl}
: ${GIT_REF:=master}
: ${LOCAL_SOURCE:=/tmp/${COMPONENT}}

function fetch_source_from_uri {
    curl ${TARBALL_URI} -o ${TMPDIR}/${COMPONENT}.tar
}

function fetch_source_from_git {
    # NOTE(pbourke): do a shallow clone to master only, unless a specific ref is
    # required
    if [ -z ${GIT_REF} ]; then
        git clone --depth=1 ${CLONE_FROM} ${TMPDIR}/${COMPONENT}
    else
        git clone ${CLONE_FROM} ${TMPDIR}/${COMPONENT}
        git --git-dir ${TMPDIR}/${COMPONENT}/.git \
            --work-tree ${TMPDIR}/${COMPONENT}/ \
            checkout ${GIT_REF}
    fi
    tar -cf ${TMPDIR}/${COMPONENT}.tar -C ${TMPDIR} ${COMPONENT}
}

function fetch_source_from_local {
    tar -cf ${TMPDIR}/${COMPONENT}.tar \
        -C $(dirname ${LOCAL_SOURCE}) ${COMPONENT}
}

case ${SOURCE_INSTALL_METHOD} in
    curl)
        fetch_source_from_uri
        ;;
    git)
        fetch_source_from_git
        ;;
    local)
        fetch_source_from_local
        ;;
    *)
        cat << EOF
Unknown install method '${SOURCE_INSTALL_METHOD}'. Please check the value of
\$SOURCE_INSTALL_METHOD in .buildconf
EOF
        exit 1
        ;;
esac
