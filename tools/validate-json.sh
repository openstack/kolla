#!/bin/bash
set -e

TMPFILE=$(mktemp)
ret=0

function clean {
    rm -f ${TMPFILE}
}
trap clean EXIT

for f in $(find docker/ -type f -name '*.json');do
    jsonlint -s ${f} >${TMPFILE}
    egrep -q 'has errors$' ${TMPFILE} && { cat ${TMPFILE}; ret=1 ;}
done

cat ${TMPFILE}

exit ${ret}
