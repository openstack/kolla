#!/bin/bash

# Bootstrap and exit if KOLLA_BOOTSTRAP variable is set. This catches all cases
# of the KOLLA_BOOTSTRAP variable being set, including empty.
if [[ "${!KOLLA_BOOTSTRAP[@]}" ]]; then
    chown -R ironic: /tftpboot
    for pxe_file in /var/lib/tftpboot/pxelinux.0 /var/lib/tftpboot/chain.c32 /usr/lib/syslinux/pxelinux.0 \
                    /usr/lib/syslinux/chain.c32 /usr/lib/PXELINUX/pxelinux.0 \
                    /usr/lib/syslinux/modules/bios/chain.c32; do
        if [[ -e "$pxe_file" ]]; then
            cp "$pxe_file" /tftpboot
        fi
    done
    exit 0
fi
