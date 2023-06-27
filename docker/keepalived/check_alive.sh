#!/bin/bash

# This will return 0 when it successfully passes all checks for all daemons
# Failures return 1

declare -A check_results
final_result=0

if [ -d "/checks" ]; then
    CHECKS=$(find /checks -type f)
fi

if [ "${CHECKS}" ]; then
    # Store results
    for check in ${CHECKS}; do
        # Run check but do not print stderr
        # as single check can be executed manually to see the result
        ${check} 2>/dev/null
        check_results[${check}]=$?
    done

    # Print results and save the final result
    for i in "${!check_results[@]}"; do
        if [ "${check_results[$i]}" == "0" ]; then
            echo "Keepalived check script ${i} succeeded."
        else
            final_result=1
            echo "Keepalived check script ${i} failed."
        fi
    done

    exit ${final_result}
fi
