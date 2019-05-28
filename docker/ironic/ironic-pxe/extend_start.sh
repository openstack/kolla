#!/bin/bash


function prepare_pxe {
    chown -R ironic: /tftpboot
    for pxe_file in /var/lib/tftpboot/pxelinux.0 /var/lib/tftpboot/chain.c32 /usr/lib/syslinux/pxelinux.0 \
                    /usr/lib/syslinux/chain.c32 /usr/lib/PXELINUX/pxelinux.0 \
                    /usr/lib/syslinux/modules/bios/chain.c32 /usr/lib/syslinux/modules/bios/ldlinux.c32; do
        if [[ -e "$pxe_file" ]]; then
            cp "$pxe_file" /tftpboot
        fi
    done
}

function prepare_ipxe {
    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        cp /usr/lib/ipxe/{undionly.kpxe,ipxe.efi} /tftpboot
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|oraclelinux|rhel ]]; then
        cp /usr/share/ipxe/{undionly.kpxe,ipxe.efi} /tftpboot
    fi
}

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    prepare_pxe
    prepare_ipxe
    exit 0
fi

if [[ "${ironic_arch}" =~ aarch64 ]]; then
    modules="boot chain configfile efinet ext2 fat gettext help hfsplus loadenv \
    lsefi normal part_gpt part_msdos read search search_fs_file search_fs_uuid \
    search_label terminal terminfo tftp linux"

    if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
        grub-mkimage -v -o /tftpboot/grubaa64.efi -O arm64-efi -p "grub" $modules
    elif [[ "${KOLLA_BASE_DISTRO}" =~ centos|oraclelinux|rhel ]]; then
        grub2-mkimage -v -o /tftpboot/grubaa64.efi -O arm64-efi -p "EFI/centos" $modules
    fi
fi

# NOTE(pbourke): httpd will not clean up after itself in some cases which
# results in the container not being able to restart. (bug #1489676, 1557036)
if [[ "${KOLLA_BASE_DISTRO}" =~ debian|ubuntu ]]; then
    # Loading Apache2 ENV variables
    . /etc/apache2/envvars
    install -d /var/run/apache2/
    rm -rf /var/run/apache2/*
else
    rm -rf /var/run/httpd/* /run/httpd/* /tmp/httpd*
fi
