#!/bin/bash

status=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8888/v1/queues)

if [[ $status -ne 200 && $status -ne 204 ]]; then
    echo "ERROR($status): queue list failed"
    exit $status
fi

exit 0
