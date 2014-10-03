#!/bin/bash
set -e
ret=0

# For MacOSX users the freebsd's mktemp by default behave diferently,
# installing the coreutils from brew would give you this but that would be
# renamed to gmktemp to don't conflict with the stand mktemp, so let just use
# that if available.
if type -p gmktemp &>/dev/null; then
    TMPFILE=$(gmktemp)
else
    TMPFILE=$(mktemp)
fi

function clean {
    rm -f ${TMPFILE}
}
trap clean EXIT

linter=jsonlint
type -p jsonlint &>/dev/null || linter=python

for f in $(find docker -type f -name '*.json');do
    if [[ ${linter} == jsonlint ]];then
        jsonlint -s ${f} >${TMPFILE}
        egrep -q 'has errors$' ${TMPFILE} && { cat ${TMPFILE}; ret=1 ;}
    else
        python -m json.tool ${f} &>/dev/null || { echo "$f: has json errors"; ret=1; }
    fi
done

cat ${TMPFILE}

exit ${ret}
