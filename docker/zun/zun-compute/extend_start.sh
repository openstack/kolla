#!/bin/bash

gid=$(stat -c "%g" /var/run/docker.sock)
sudo groupadd --force --gid $gid docker
sudo usermod -aG docker zun
