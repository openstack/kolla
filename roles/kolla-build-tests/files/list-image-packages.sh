#!/bin/bash

# List the packages installed in each kolla image, one <image>.txt file per
# image with one package name per line.
#
# Usage: list-image-packages.sh <container engine> <base distro> <output dir>

set -o errexit
set -o nounset
set -o pipefail

engine=$1
base_distro=$2
outdir=$3

case "${base_distro}" in
    rocky)
        query=(rpm -qa --qf '%{NAME}\n')
        ;;
    debian|ubuntu)
        query=(dpkg-query -W -f '${Package}\n')
        ;;
    *)
        echo "Unsupported base distro: ${base_distro}" >&2
        exit 1
        ;;
esac

list_image() {
    local id=$1
    local name
    name=$(sudo "${engine}" image inspect \
        --format '{{ index .Config.Labels "name" }}' "${id}")
    if ! sudo "${engine}" run --rm --network none \
            --entrypoint "${query[0]}" "${id}" "${query[@]:1}" \
            > "${outdir}/${name}.txt"; then
        echo "Failed to list packages in ${name}" >&2
        rm -f "${outdir}/${name}.txt"
    fi
}

mkdir -p "${outdir}"

# Only kolla images carry the kolla_version label.
images=$(sudo "${engine}" images --filter label=kolla_version \
    --format '{{ .ID }}' | sort -u)

running=0
for id in ${images}; do
    list_image "${id}" &
    running=$((running + 1))
    if [[ ${running} -ge 8 ]]; then
        wait -n || true
        running=$((running - 1))
    fi
done
wait
