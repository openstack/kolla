#!/bin/bash

# ref: https://github.com/nfs-ganesha/nfs-ganesha/issues/114
function init_rpc {
  rpcbind || return 0
  rpc.statd -L || return 0
  rpc.idmapd || return 0
  sleep 1
}

init_rpc
