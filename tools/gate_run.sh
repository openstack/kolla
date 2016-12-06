#!/bin/bash

tools/setup_gate.sh
tox -e $ACTION-$BASE_DISTRO-$INSTALL_TYPE
