#!/bin/bash

# This script works as debian quilt patch.
# So, patch files included in /patches/series
# are applied and information what was applied
# is stored in /etc/kolla/patched.
#
# No more, no less :)

cd /

# If exist /patches/series
# let's try to apply patches
if [ -e "/patches/series" ]; then
    # If there is /patches/series.applied
    # then it means previous run already applied
    # some patches - from another intermediate container
    #
    # So, let's add patches again to /patches/series
    # and let's script to handle it
    if [ -e "/patches/series.applied" ]; then
        grep -v '^#' /patches/series.applied > /tmp/series.tmp
        grep -v '^#' /patches/series >> /tmp/series.tmp
        rm -f /patches/series
        mv /tmp/series.tmp /patches/series
    fi
    touch /etc/kolla/patched
    for patchfile in $(grep -v '^#' /patches/series); do
        # If patch is not applied, try to apply it, otherwise
        # inform user that patchfile is already applied
        if ! grep -q "$patchfile" /etc/kolla/patched; then
            echo "[i] Applying /patches/${patchfile}"
            patch -p0 --fuzz=0 --ignore-whitespace < /patches/${i}/${patchfile}
            # If apply patch was successful inform user,
            # otherwise fail build process and inform user
            # to check/fix patch
            if [ $? -eq 0 ]; then
                echo "[i] Applied /patches/${patchfile}" >> /etc/kolla/patched
            else
                echo "[i] Patch /patches/${patchfile} failed, please fix your patchfiles."
                exit 1
            fi
        else
            echo "[i] /patches/${patchfile} already applied."
        fi
    done
    # Ignore files which are commented and move
    # to /patches/series.applied as /patch/series
    # can be potentially replaced by another files
    # from different intermediate container
    grep -v '^#' /patches/series > /patches/series.applied
    rm -f /patches/series
else
    echo "[i] No series file found, nothing to patch."
fi
