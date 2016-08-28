#!/usr/bin/env python

# Copyright 2015 Paul Bourke
#
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
This script is a simple wrapper used to create and rebalance Swift ring files.
"""

import argparse
import subprocess  # nosec
import sys


def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--ring-file",
                        required=True,
                        help="Path to ring file")
    parser.add_argument("-p", "--part-power",
                        required=True,
                        help="Part power")
    parser.add_argument("-r", "--num-replicas",
                        required=True,
                        help="Number of replicas")
    parser.add_argument("-m", "--min-part-hours",
                        required=True,
                        help="Min part hours")
    parser.add_argument("-H", "--hosts",
                        required=True,
                        help="Hosts in the ring, comma delimited")
    parser.add_argument("-w", "--weights",
                        required=True,
                        help="Weight of each host, comma delimited")
    parser.add_argument("-d", "--devices",
                        required=True,
                        help="Device on each host, comma delimited")
    parser.add_argument("-z", "--zones",
                        required=True,
                        help="Zone of each host, comma delimited")
    return parser.parse_args()


def run_cmd(cmd):
    print(' '.join(cmd))
    # NOTE(sdake): [0] we expect Operators to run this command and for their
    # environment to be properly secured.  Since this is not a network
    # facing tool, there is no risk of untrusted input.
    subprocess.call(cmd)  # nosec [0]


def run(args):
    hosts = args.hosts.split(',')
    weights = args.weights.split(',')
    zones = args.zones.split(',')
    devices = args.devices.split(',')
    if not (len(hosts) == len(weights) == len(zones) == len(devices)):
        print('Error: an equal amount of hosts, devices, weights, '
              'and zones are required')
        sys.exit(1)

    run_cmd(['swift-ring-builder',
             args.ring_file,
             'create',
             args.part_power,
             args.num_replicas,
             args.min_part_hours])

    for i in range(len(hosts)):
        run_cmd(['swift-ring-builder',
                 args.ring_file,
                 'add',
                 'z{}-{}/{}'.format(zones[i], hosts[i], devices[i]),
                 weights[i]])

    run_cmd(['swift-ring-builder', args.ring_file, 'rebalance'])


def main():
    args = setup_args()
    run(args)


if __name__ == "__main__":
    main()
