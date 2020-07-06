#!/bin/bash

# Move to top level directory
REAL_PATH=$(realpath $0)
cd "$(dirname "$REAL_PATH")/.."

RES=0

generate_templates () {
    echo Generating templates for $distro
    tools/build.py --template-only --type binary --base $distro --work-dir=$tmpdir
}

check_for_errors () {
    regex=$1
    # Look for all rendered Dockerfile.
    # TODO(mwhahaha): Skip kolla-toolbox for now as it's dependent on specific
    # set of pip installed items.
    find $tmpdir/docker -not -path "*kolla-toolbox*" -name Dockerfile -print0 |
        xargs -0 egrep --color "$regex"
    # NOTE(mandre) grep returns status code of 1 if the expression isn't found
    # xargs returns with status 123 when the command invocation returns with an
    # exit status 1-125, this is what we should be looking for as our "everything
    # is good" code.
    if [ $? -ne 123 ]; then
        RES=1
    fi
}

echo Looking for forbidden instructions in binary image templates

for distro in debian ubuntu centos rhel; do
    tmpdir=$(mktemp -d kolla-templates.XXXXXX --tmpdir)
    generate_templates
    check_for_errors "gem .*install"
    check_for_errors "pip .*install"
    check_for_errors "npm .*install"
    check_for_errors "git .*clone"
    check_for_errors "wget"
    check_for_errors "curl"
    rm -r $tmpdir
done

if [ $RES -eq 1 ]; then
    echo "ERROR Found forbidden instructions in binary image templates"
fi
# Let's not make it fail pep8 job for now
#exit $RES
