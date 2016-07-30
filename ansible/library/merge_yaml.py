#!/usr/bin/python

# Copyright 2015 Sam Yaple
# Copyright 2016 intel
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
module: merge_yaml
short_description: Merge yaml-style configs
description:
     - PyYAML is used to merge several yaml files into one
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
author: Sean Mooney
'''

EXAMPLES = '''
Merge multiple yaml files:

- hosts: localhost
  tasks:
    - name: Merge yaml files
      merge_yaml:
        sources:
          - "/tmp/default.yml"
          - "/tmp/override.yml"
        dest:
          - "/tmp/out.yml"
'''
