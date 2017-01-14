#!/bin/bash

set -o errexit
set -o xtrace

function collect_logs {
    set +o errexit
    mkdir -p logs

    # copy system log

    sudo cp -r /var/log logs/system_log

    if which journalctl ; then
        # the journal gives us syslog() and kernel output, so is like
        # a concatenation of the above.
        sudo journalctl --no-pager | sudo tee logs/syslog.txt > /dev/null
        sudo journalctl --no-pager -u docker.service | sudo tee logs/docker.log > /dev/null
    else
        # assume rsyslog
        sudo cp /var/log/syslog logs/syslog.txt
        sudo cp /var/log/kern.log logs/kern_log.txt
        sudo cp /var/log/upstart/docker.log logs/docker.log
    fi

    if [[ -d /var/lib/docker/volumes/kolla_logs/_data ]]; then
        sudo cp -r /var/lib/docker/volumes/kolla_logs/_data logs/kolla_logs
    fi

    # sudo config
    sudo cp -r /etc/sudoers.d logs/
    sudo cp /etc/sudoers logs/sudoers.txt

    df -h > logs/df.txt
    free  > logs/free.txt
    sudo parted -l | sudo tee logs/parted-l.txt > /dev/null
    mount > logs/mount.txt
    env > logs/env.txt

    if [ `command -v dpkg` ]; then
        dpkg -l | sudo tee logs/dpkg-l.txt > /dev/null
    fi
    if [ `command -v rpm` ]; then
        rpm -qa | sudo tee logs/rpm-qa.txt > /dev/null
    fi

    # final memory usage and process list
    ps -eo user,pid,ppid,lwp,%cpu,%mem,size,rss,cmd > logs/ps.txt

    # docker related information
    (docker info && docker images && docker ps -a) > logs/docker-info.txt

    sudo cp -r /etc/kolla logs/kolla_configs

    # fix the permissions for logs folder
    sudo chmod -R 777 logs

    # rename files to .txt; this is so that when displayed via
    # logs.openstack.org clicking results in the browser shows the
    # files, rather than trying to send it to another app or make you
    # download it, etc.

    # firstly, rename all .log files to .txt files
    for f in $(find logs -name "*.log"); do
        sudo mv $f ${f/.log/.txt}
    done

    # append .txt to all kolla config file
    find logs/kolla_configs -type f -exec mv '{}' '{}'.txt \;

    # Compress all text logs
    find logs -iname '*.txt' -execdir gzip -9 {} \+
    find logs -iname '*.json' -execdir gzip -9 {} \+

    set -o errexit
}

function pack_registry {
    BRANCH=$(echo $ZUUL_REFNAME | cut -d/ -f2)
    sudo mkdir "images"
    FILENAME=${BASE_DISTRO}-${INSTALL_TYPE}-registry-${BRANCH}.tar.gz
    sudo docker stop registry
    sudo tar -zcf "images/$FILENAME" -C /tmp/kolla_registry .
    sudo docker start registry
    sudo chmod 755 -R images
}


trap collect_logs EXIT

tools/setup_gate.sh
tox -e $ACTION-$BASE_DISTRO-$INSTALL_TYPE

if [[ -n $PACK_REGISTRY ]] && [[ $ACTION == "build" ]]; then
    pack_registry
fi
