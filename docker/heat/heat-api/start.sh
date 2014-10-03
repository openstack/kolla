#!/bin/bash
set -e

: ${IP_ADDRESS:=$IP_ADDRESS}

if [ -z "$IP_ADDRESS" ]; then
	echo >&2 'error: IP_ADDRESS is not set.'
	echo >&2 '   Be sure to set IP_ADDRESS so it can be placed in heat configurations'
	exit 1
fi


exec /usr/bin/heat-api
