#!/bin/bash

. /opt/kolla/kolla-common.sh

check_required_vars SWIFT_HASH_PATH_SUFFIX

cfg=/etc/swift/swift.conf

crudini --set $cfg swift-hash swift_hash_path_suffix "${SWIFT_HASH_PATH_SUFFIX}"
