#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Command-line utility to get the IP address from the newest DHCP lease.

It's written for using with vagrant-hostmanager and vagrant-libvirt plugins.
Vagrant-hostmanager by default fetches only IP addresses from eth0 interfaces
on VM-s. Therefore, the first purpose of this utility is to be able to fetch
the address also from the other interfaces.

Libvirt/virsh only lists all DHCP leases for the given network with timestamps.
DHCP leases have their expiration time, but are not cleaned up after destroying
VM. If someone destroys and sets up the VM with the same hostname, we have
many DHCP leases for the same hostname and we have to look up for timestamp.
That's the second purpose of this script.
"""

import argparse
import csv
import functools
import operator
import xml.etree.ElementTree as etree

import libvirt


class NoPrivateDHCPInterfaceException(Exception):
    pass


class NoDHCPLeaseException(Exception):
    pass


def libvirt_conn(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        conn = libvirt.openReadOnly('qemu:///system')
        return f(conn, *args, **kwargs)
    return wrapper


@libvirt_conn
def get_vir_network_dhcp_lease(conn, vm_name):
    """Libvirt since 1.2.6 version provides DHCPLeases method in virNetwork.

    That's the current official way for getting DHCP leases and this
    information isn't stored anywhere else anymore.
    """
    domain_name = 'vagrant_' + vm_name
    mac_address = get_mac_address(conn, domain_name)

    network = conn.networkLookupByName('vagrant-private-dhcp')
    dhcp_leases = libvirt.virNetwork.DHCPLeases(network)

    vm_dhcp_leases = [lease for lease in dhcp_leases
                      if lease['mac'] == mac_address]

    newest_vm_dhcp_lease = sorted(vm_dhcp_leases,
                                  key=operator.itemgetter('expirytime'),
                                  reverse=True)[0]['ipaddr']
    return newest_vm_dhcp_lease


def get_mac_address(conn, domain_name):
    """Get MAC address from domain XML."""
    domain = conn.lookupByName(domain_name)
    domain_xml = domain.XMLDesc()
    domain_tree = etree.fromstring(domain_xml)
    devices = domain_tree.find('devices')
    interfaces = devices.iterfind('interface')

    for interface in interfaces:
        source = interface.find('source')
        if source is None or source.get('network') != 'vagrant-private-dhcp':
            continue
        mac_element = interface.find('mac')
        mac_address = mac_element.get('address')
        return mac_address

    raise NoPrivateDHCPInterfaceException()


@libvirt_conn
def get_dnsmasq_dhcp_lease(conn, vm_name):
    """In libvirt under 1.2.6 DHCP leases are stored in file.

    There is no API for DHCP leases yet.
    """
    domain_name = 'vagrant_' + vm_name
    mac_address = get_mac_address(conn, domain_name)

    with open(
        '/var/lib/libvirt/dnsmasq/vagrant-private-dhcp.leases'
    ) as leases_file:
        reader = csv.reader(leases_file, delimiter=' ')
        for row in reader:
            lease_mac, lease_ip, lease_vm_name = row[1:4]
            if not (lease_mac == mac_address and lease_vm_name == vm_name):
                continue
            return lease_ip

    raise NoDHCPLeaseException()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('vm_name', help='Name of the virtual machine')

    args = parser.parse_args()
    vm_name = args.vm_name

    if libvirt.getVersion() >= 1002006:
        newest_dhcp_lease = get_vir_network_dhcp_lease(vm_name)
    else:
        newest_dhcp_lease = get_dnsmasq_dhcp_lease(vm_name)

    print(newest_dhcp_lease)


if __name__ == '__main__':
    main()
