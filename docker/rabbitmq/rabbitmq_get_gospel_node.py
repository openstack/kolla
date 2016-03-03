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
import re
import subprocess
import traceback


def convert_erlang_to_json(term):
    term = re.sub('[\s+]', '', term)
    term = re.sub('([<>].*?)}', r'"\1"}', term)
    term = re.sub('{([a-z].*?),', r'{"\1":', term)
    term = re.sub(':([a-z].*?)}', r':"\1"}', term)
    return json.loads(term)


def main():
    try:
        raw_status = subprocess.check_output(
            "rabbitmqctl eval 'rabbit_clusterer:status().'",
            shell=True, stderr=subprocess.STDOUT
        )
        if "Rabbit is running in cluster configuration" not in raw_status:
            raise AttributeError
        status = convert_erlang_to_json(
            '\n'.join(raw_status.split('\n')[1:-3])
        )

        gospel_node = None
        for msg in status:
            if 'gospel' in msg:
                gospel_node = msg['gospel']['node'].split('@')[1]
        if gospel_node is None:
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
