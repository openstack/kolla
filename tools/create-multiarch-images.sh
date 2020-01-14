#!/bin/bash

# This script takes aarch64 and x86_64 images from our publish jobs and makes
# multiarch containers so users of any of those architectures can pull them.

TARGET=${NAMESPACE}/${DISTRO}-${TYPE}
TMP=$(mktemp -d)

for arch in aarch64 x86_64; do
    tools/build.py --base ${DISTRO} --type ${TYPE} --base-arch $arch --list-images|sed -e 's/^.* : //g'|sort >${TMP}/images-$arch
done

comm -12 ${TMP}/images-aarch64 ${TMP}/images-x86_64 >${TMP}/list-of-common-images
comm -13 ${TMP}/images-aarch64 ${TMP}/images-x86_64 >${TMP}/list-of-x86_64-only-images
comm -23 ${TMP}/images-aarch64 ${TMP}/images-x86_64 >${TMP}/list-of-aarch64-only-images


for image_name in $(cat ${TMP}/list-of-common-images); do
    docker manifest create ${TARGET}-${image_name}:${TAG} ${TARGET}-${image_name}:${TAG}-aarch64 ${TARGET}-${image_name}:${TAG}-x86_64
done

for image_name in $(cat ${TMP}/list-of-x86_64-only-images); do
    docker manifest create ${TARGET}-${image_name}:${TAG} ${TARGET}-${image_name}:${TAG}-x86_64
done

for image_name in $(cat ${TMP}/list-of-aarch64-only-images); do
    docker manifest create ${TARGET}-${image_name}:${TAG} ${TARGET}-${image_name}:${TAG}-aarch64
done

for image_name in $(cat ${TMP}/list-of-*); do
    docker manifest push ${TARGET}-${image_name}:${TAG}
done
