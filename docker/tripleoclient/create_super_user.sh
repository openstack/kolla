#!/bin/bash
# This is a useful entrypoint/cmd if you wish to run commands in a container
# in an existing users $HOME directory
# For example: docker run -ti -e USER=stack -e UID=1000 --privileged=true --volume=/home/stack/:/home/stack/ tripleoclient:latest /usr/local/bin/create_super_user.sh

if [ -n "$USER" -a -n "$UID" ]; then
    useradd "$USER" -u "$UID" -M
cat >> /etc/sudoers <<EOF_CAT
$USER ALL=(ALL) NOPASSWD:ALL
EOF_CAT
    su -l $USER
    export TERM="xterm"
    alias ls='ls --color=auto'
    /bin/bash
else
    echo "Please set valid $USER and $UID env variables."
    exit 1
fi
