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

# This file is a barebones file needed to file a gap until Ansible 2.0. No
# error checking, no deletions, no updates. Idempotent creation only.

# If you look closely, you will see we arent _really_ using the shade module
# we just use it to slightly abstract the authentication model. As patches land
# in upstream shade we will be able to use more of the shade module. Until then
# if we want to be 'stable' we really need to be using it as a passthrough

import shade


def main():
    argument_spec = openstack_full_argument_spec(
        description=dict(required=True, type='str'),
        service_name=dict(required=True, type='str'),
        service_type=dict(required=True, type='str'),
        url=dict(required=True, type='str'),
        interface=dict(required=True, type='str'),
        endpoint_region=dict(required=True, type='str')
    )
    module = AnsibleModule(argument_spec)

    try:
        description = module.params.pop('description')
        service_name = module.params.pop('service_name')
        service_type = module.params.pop('service_type')
        url = module.params.pop('url')
        interface = module.params.pop('interface')
        endpoint_region = module.params.pop('endpoint_region')

        changed = False
        service = None
        endpoint = None

        cloud = shade.operator_cloud(**module.params)

        for _service in cloud.keystone_client.services.list():
            if _service.type == service_type:
                service = _service

        if service is not None:
            for _endpoint in cloud.keystone_client.endpoints.list():
                if _endpoint.service_id == service.id and \
                   _endpoint.interface == interface:
                    endpoint = _endpoint
        else:
            service = cloud.keystone_client.services.create(
                name=service_name,
                service_type=service_type,
                description=description)

        if endpoint is None:
            changed = True
            cloud.keystone_client.endpoints.create(
                service=service.id,
                url=url,
                interface=interface,
                region=endpoint_region)

        module.exit_json(changed=changed)
    except Exception as e:
        module.exit_json(failed=True, changed=True, msg=e)

# import module snippets
from ansible.module_utils.basic import *  # noqa
from ansible.module_utils.openstack import *  # noqa
if __name__ == '__main__':
    main()
