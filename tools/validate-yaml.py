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

import argparse
import logging
import sys
import yaml


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('input', nargs='*')
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig()
    res = 0

    for filename in args.input:
        with open(filename) as fd:
            try:
                yaml.safe_load(fd)
            except yaml.error.YAMLError as error:
                res = 1
                logging.error('%s failed validation: %s',
                              filename, error)

    sys.exit(res)

if __name__ == '__main__':
    main()
