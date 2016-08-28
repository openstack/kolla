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

import json
import subprocess  # nosec
import traceback


def extract_gospel_node(term):
    return term.split("@")[1].translate(None, "\'\"{},")


def main():
    try:
        # TODO(pbourke): see if can get gospel node without requiring shell
        raw_status = subprocess.check_output(
            "/usr/sbin/rabbitmqctl eval 'rabbit_clusterer:status().'",
            shell=True, stderr=subprocess.STDOUT  # nosec: this command appears
                                                  # to require a shell to work
        )
        if "Rabbit is running in cluster configuration" not in raw_status:
            raise AttributeError
        gospel_line = [
            line for line in raw_status.split('\n') if 'gospel' in line
        ][0]
        gospel_node = extract_gospel_node(gospel_line)
        if not gospel_node:
            raise AttributeError
    except AttributeError:
        result = {
            'failed': True,
            'error': raw_status,
            'changed': True
        }
    except Exception:
        result = {
            'failed': True,
            'error': traceback.format_exc(),
            'changed': True
        }
    else:
        result = {
            'failed': False,
            'hostname': gospel_node,
            'changed': False
        }

    print(json.dumps(result))


if __name__ == '__main__':
    main()
