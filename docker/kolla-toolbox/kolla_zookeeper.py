#!/usr/bin/python

#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib

import kazoo.client
import kazoo.exceptions


@contextlib.contextmanager
def zk_connection(zk_host, zk_port):
    zk = kazoo.client.KazooClient(hosts='{}:{}'.format(zk_host, zk_port))
    zk.start()
    yield zk
    zk.stop()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            zk_host=dict(required=True, type='str'),
            zk_port=dict(required=True, type='str'),
            path=dict(required=True, type='str'),
            value=dict(required=False, default=None, type='str')
        )
    )

    try:
        zk_host = module.params.pop('zk_host')
        zk_port = module.params.pop('zk_port')
        path = module.params.pop('path')
        value = module.params.pop('value')

        changed = False
        with zk_connection(zk_host, zk_port) as zk:
            try:
                zk.get(path)
            except kazoo.exceptions.NoNodeError:
                if value is None:
                    zk.create(path, makepath=True)
                else:
                    zk.create(path, value=value.encode(), makepath=True)
                changed = True

        module.exit_json(changed=changed)
    except Exception as e:
        module.exit_json(failed=True, changed=True, msg=e)


# import module snippets
from ansible.module_utils.basic import *  # noqa
if __name__ == '__main__':
    main()
