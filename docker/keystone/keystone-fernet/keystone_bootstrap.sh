#!/bin/bash

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

USERNAME=$1
GROUP=$2

function fail_json {
    echo '{"failed": true, "msg": "'$1'", "changed": true}'
    exit 1
}

function exit_json {
    echo '{"failed": false, "changed": '"${changed}"'}'
}

changed="false"
keystone_bootstrap=$(keystone-manage --config-file /etc/keystone/keystone.conf fernet_setup --keystone-user ${USERNAME} --keystone-group ${GROUP} 2>&1)
if [[ $? != 0 ]]; then
    fail_json "${keystone_bootstrap}"
fi

changed=$(echo "${keystone_bootstrap}" | awk '
    /Key repository is already initialized/ {count++}
    END {
        if (count == 1) changed="true"; else changed="false"
        print changed
    }'
)

exit_json
