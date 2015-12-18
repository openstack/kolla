#!/usr/bin/python

# Copyright 2015 Sam Yaple
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

DOCUMENTATION = '''
---
module: merge_configs
short_description: Merge ini-style configs
description:
     - ConfigParser is used to merge several ini-style configs into one
options:
  dest:
    description:
      - The destination file name
    required: True
    type: str
  sources:
    description:
      - A list of files on the destination node to merge together
    default: None
    required: True
    type: str
author: Sam Yaple
'''

EXAMPLES = '''
Merge multiple configs:

- hosts: database
  tasks:
    - name: Merge configs
      merge_configs:
        sources:
          - "/tmp/config_1.cnf"
          - "/tmp/config_2.cnf"
          - "/tmp/config_3.cnf"
        dest:
          - "/etc/mysql/my.cnf"
'''
