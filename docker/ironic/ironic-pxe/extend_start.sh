#!/bin/bash


# For x86 legacy BIOS boot mode
function prepare_pxe_pxelinux {
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        cp /usr/lib/PXELINUX/pxelinux.0 \
           /usr/lib/syslinux/modules/bios/{chain.c32,ldlinux.c32} \
           ${TFTPBOOT_PATH}/
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|rocky ]]; then
        if [[ "${TFTPBOOT_PATH}" != /tftpboot ]]; then
            cp /tftpboot/{pxelinux.0,chain.c32,ldlinux.c32} \
               ${TFTPBOOT_PATH}/
        fi
    fi
}

# For UEFI boot mode
function prepare_pxe_grub {
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu  ]]; then
        shim_src_file="/usr/lib/shim/shim*64.efi.signed"
        grub_src_file="/usr/lib/grub/*-efi-signed/grubnet*64.efi.signed"
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|rocky ]]; then
        shim_src_file="/boot/efi/EFI/${KOLLA_BASE_DISTRO}/shim*64.efi"
        grub_src_file="/boot/efi/EFI/${KOLLA_BASE_DISTRO}/grub*64.efi"
    fi

    if [[ "${KOLLA_BASE_ARCH}" == "x86_64" ]]; then
        shim_dst_file="bootx64.efi"
        grub_dst_file="grubx64.efi"
    elif [[ "${KOLLA_BASE_ARCH}" == "aarch64" ]]; then
        shim_dst_file="bootaa64.efi"
        grub_dst_file="grubaa64.efi"
    fi

    cp $shim_src_file ${TFTPBOOT_PATH}/$shim_dst_file
    cp $grub_src_file ${TFTPBOOT_PATH}/$grub_dst_file
}

function prepare_ipxe {
    # NOTE(mgoddard): Ironic uses snponly.efi as the default for
    # uefi_ipxe_bootfile_name since Xena. In Wallaby and earlier releases it
    # was ipxe.efi. Ensure that both exist, using symlinks where the files are
    # named differently to allow the original names to be used in ironic.conf.
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        cp /usr/lib/ipxe/{undionly.kpxe,ipxe.efi} ${TFTPBOOT_PATH}/
        # NOTE(mgoddard): The 'else' can be removed  when snponly.efi is
        # available in Jammy 22.04.
        if [[ -f /usr/lib/ipxe/snponly.efi ]]; then
            cp /usr/lib/ipxe/snponly.efi ${TFTPBOOT_PATH}/snponly.efi
        elif [[ ! -e ${TFTPBOOT_PATH}/snponly.efi ]]; then
            ln -s ${TFTPBOOT_PATH}/ipxe.efi ${TFTPBOOT_PATH}/snponly.efi
        fi
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|rocky ]]; then
        cp /usr/share/ipxe/{undionly.kpxe,ipxe*.efi} ${TFTPBOOT_PATH}/
        if [[ ! -e ${TFTPBOOT_PATH}/ipxe.efi ]]; then
            ln -s ${TFTPBOOT_PATH}/ipxe-${KOLLA_BASE_ARCH}.efi ${TFTPBOOT_PATH}/ipxe.efi
        fi
        if [[ ! -e ${TFTPBOOT_PATH}/snponly.efi ]]; then
            ln -s ${TFTPBOOT_PATH}/ipxe-snponly-${KOLLA_BASE_ARCH}.efi ${TFTPBOOT_PATH}/snponly.efi
        fi
    fi
}

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    mkdir -p ${TFTPBOOT_PATH} ${HTTPBOOT_PATH}
    chown ironic: ${TFTPBOOT_PATH} ${HTTPBOOT_PATH}
    prepare_pxe_pxelinux
    prepare_pxe_grub
    prepare_ipxe
    exit 0
fi

# Template out a TFTP map file, using the TFTPBOOT_PATH variable.
envsubst < /map-file-template > /map-file

. /usr/local/bin/kolla_httpd_setup
