#!/usr/bin/env bash
#
# This script generates the minimal environment variable doc

# Move to top level directory
REAL_PATH=$(python -c "import os,sys;print os.path.realpath('$0')")
cd "$(dirname "$REAL_PATH")/.."

DOC=docs/minimal-environment-vars.md
DOCKERDIR="docker"
# BASE and TYPE can be hard coded to centos and rdo since the required vars will always be the same
BASE="centos"
TYPE="rdo"

function write_header {
    local header=$1
    header=${header^}
    header=$(echo ${header} | sed -e 's/-app//')
    echo -e "\n# $header\n" >> "$DOC"
}

function write_env_var {
    local env_var=$1
    if [ -z "$env_var" ]; then
        echo "" >> "$DOC"
    else
        env_var=${env_var%=*}
        echo "    $env_var" >> "$DOC"
    fi
}

function find_vars {
    local img_location=$1
    local empty=true
    scripts=$(find ${img_location} -name *.sh | sort -t / -k 4)

    for script in $scripts; do
        local vars=$(awk '/^\s*check_required_vars/,/([^\\]\s*$)/' $script)
        vars=$(echo "$vars" | sed 's/check_required_vars//' | sed 's/\\//g')

        if [ ! -z "$vars" ]; then
            empty=false
            for v in $vars; do
                write_env_var $v
            done
        fi
    done

    if $empty; then
        echo "    None" >> "$DOC"
    fi
}

cat > $DOC <<EOF
# Environment Variables

In order for each service to function, there is a minimum set of required variables that need to be plugged into the environment.  Below is the list of variables that is needed for each service to run in a minimal setting.
EOF

declare -a startsh
startsh=$(find "${DOCKERDIR}/${BASE}/${TYPE}/" -name Dockerfile | sort -t / -k 4 | grep -v data)

for start_script in $startsh; do
    if [ ! "$(dirname $start_script | xargs basename)" == "base" ]; then
        write_header $(dirname $start_script | xargs basename)
        find_vars $(dirname $start_script) $(dirname $start_script | xargs basename)
    fi
done
