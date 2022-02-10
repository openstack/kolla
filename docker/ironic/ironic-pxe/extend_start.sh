#!/bin/bash


# For x86 legacy BIOS boot mode
function prepare_pxe_pxelinux {
    chown -R ironic: /tftpboot
    for pxe_file in /var/lib/tftpboot/pxelinux.0 /var/lib/tftpboot/chain.c32 /usr/lib/syslinux/pxelinux.0 \
                    /usr/lib/syslinux/chain.c32 /usr/lib/PXELINUX/pxelinux.0 \
                    /usr/lib/syslinux/modules/bios/chain.c32 /usr/lib/syslinux/modules/bios/ldlinux.c32; do
        if [[ -e "$pxe_file" ]]; then
            cp "$pxe_file" /tftpboot
        fi
    done
}

# For UEFI boot mode
function prepare_pxe_grub {
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu  ]]; then
        shim_src_file="/usr/lib/shim/shim*64.efi.signed"
        grub_src_file="/usr/lib/grub/*-efi-signed/grubnet*64.efi.signed"
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|rhel ]]; then
        shim_src_file="/boot/efi/EFI/centos/shim*64.efi"
        grub_src_file="/boot/efi/EFI/centos/grub*64.efi"
    fi

    if [[ "${KOLLA_BASE_ARCH}" == "x86_64" ]]; then
        shim_dst_file="bootx64.efi"
        grub_dst_file="grubx64.efi"
    elif [[ "${KOLLA_BASE_ARCH}" == "aarch64" ]]; then
        shim_dst_file="bootaa64.efi"
        grub_dst_file="grubaa64.efi"
    fi

    cp $shim_src_file /tftpboot/$shim_dst_file
    cp $grub_src_file /tftpboot/$grub_dst_file
}

function prepare_ipxe {
    # NOTE(mgoddard): Ironic uses snponly.efi as the default for
    # uefi_ipxe_bootfile_name since Xena. In Wallaby and earlier releases it
    # was ipxe.efi. Ensure that both exist, using symlinks where the files are
    # named differently to allow the original names to be used in ironic.conf.
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        cp /usr/lib/ipxe/{undionly.kpxe,ipxe.efi} /tftpboot
        # NOTE(mgoddard): The 'else' can be removed  when snponly.efi is
        # available in Jammy 22.04.
        if [[ -f /usr/lib/ipxe/snponly.efi ]]; then
            cp /usr/lib/ipxe/snponly.efi /tftpboot/snponly.efi
        elif [[ ! -e /tftpboot/snponly.efi ]]; then
            ln -s /tftpboot/ipxe.efi /tftpboot/snponly.efi
        fi
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|rhel ]]; then
        cp /usr/share/ipxe/{undionly.kpxe,ipxe*.efi} /tftpboot
        if [[ ! -e /tftpboot/ipxe.efi ]]; then
            ln -s /tftpboot/ipxe-${KOLLA_BASE_ARCH}.efi /tftpboot/ipxe.efi
        fi
        if [[ ! -e /tftpboot/snponly.efi ]]; then
            ln -s /tftpboot/ipxe-snponly-${KOLLA_BASE_ARCH}.efi /tftpboot/snponly.efi
        fi
    fi
}

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    prepare_pxe_pxelinux
    prepare_pxe_grub
    prepare_ipxe
    exit 0
fi

. /usr/local/bin/kolla_httpd_setup
