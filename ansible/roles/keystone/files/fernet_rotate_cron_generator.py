#!/usr/bin/python

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

# This module creates a list of cron intervals for a node in a group of nodes
# to ensure each node runs a cron in round robbin style.

from __future__ import print_function
import argparse
import json
import sys

MINUTE_SPAN = 1
HOUR_SPAN = 60
DAY_SPAN = 24 * HOUR_SPAN
WEEK_SPAN = 7 * DAY_SPAN


def json_exit(msg=None, failed=False, changed=False):
    if type(msg) is not dict:
        msg = {'msg': str(msg)}
    msg.update({'failed': failed, 'changed': changed})
    print(json.dumps(msg))
    sys.exit()


def generate(host_index, total_hosts, total_rotation_mins):
    min = '*'
    hour = '*'
    day = '*'
    crons = []

    if host_index >= total_hosts:
        return crons

    rotation_frequency = total_rotation_mins // total_hosts
    cron_min = rotation_frequency * host_index

    # Build crons for a week period
    if total_rotation_mins == WEEK_SPAN:
        day = cron_min // DAY_SPAN
        hour = (cron_min % DAY_SPAN) // HOUR_SPAN
        min = cron_min % HOUR_SPAN
        crons.append({'min': min, 'hour': hour, 'day': day})

    # Build crons for a day period
    elif total_rotation_mins == DAY_SPAN:
        hour = cron_min // HOUR_SPAN
        min = cron_min % HOUR_SPAN
        crons.append({'min': min, 'hour': hour, 'day': day})

    # Build crons for multiple of an hour
    elif total_rotation_mins % HOUR_SPAN == 0:
        for multiple in range(1, DAY_SPAN // total_rotation_mins + 1):
            time = cron_min
            if multiple > 1:
                time += total_rotation_mins * (multiple - 1)

            hour = time // HOUR_SPAN
            min = time % HOUR_SPAN
            crons.append({'min': min, 'hour': hour, 'day': day})

    # Build crons for multiple of a minute
    elif total_rotation_mins % MINUTE_SPAN == 0:
        for multiple in range(1, HOUR_SPAN // total_rotation_mins + 1):
            time = cron_min
            if multiple > 1:
                time += total_rotation_mins * (multiple - 1)

            min = time // MINUTE_SPAN
            crons.append({'min': min, 'hour': hour, 'day': day})

    return crons


def main():
    parser = argparse.ArgumentParser(description='''Creates a list of cron
        intervals for a node in a group of nodes to ensure each node runs
        a cron in round robbin style.''')
    parser.add_argument('-t', '--time',
                        help='Time in seconds for a token rotation cycle',
                        required=True,
                        type=int)
    parser.add_argument('-i', '--index',
                        help='Index of host starting from 0',
                        required=True,
                        type=int)
    parser.add_argument('-n', '--number',
                        help='Number of tokens that should exist',
                        required=True,
                        type=int)
    args = parser.parse_args()
    json_exit({'cron_jobs': generate(args.index, args.number, args.time)})


if __name__ == "__main__":
    main()
