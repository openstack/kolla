#!/usr/bin/python

# Copyright 2015 Intel corporation
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

import tempfile
import traceback

import shade


class SanityChecks(object):
    @staticmethod
    def keystone(cloud):
        [tenant for tenant in cloud.keystone_client.tenants.list()]

    @staticmethod
    def glance(cloud):
        with tempfile.NamedTemporaryfile(suffix='qcow2') as image:
            cloud.create_image("test", filename=image.name,
                               disk_format="qcow2", container_format="bare")
        testid = cloud.get_image_id("test")
        cloud.delete_image(testid)

    @staticmethod
    def cinder(cloud):
        [volume for volume in cloud.cinder_client.volumes.list()]

    @staticmethod
    def swift(cloud):
        [container for container in cloud.swift_client.list()]


def main():
    module = AnsibleModule(
        argument_spec=openstack_full_argument_spec(
            password=dict(required=True, type='str'),
            project=dict(required=True, type='str'),
            role=dict(required=True, type='str'),
            user=dict(required=True, type='str'),
            service=dict(required=True, type='str'),
        )
    )

    try:
        changed = True
        cloud = shade.operator_cloud(**module.params)

        getattr(SanityChecks, module.params.pop("service"))(cloud)

        module.exit_json(changed=changed)
    except Exception:
        module.exit_json(failed=True, changed=True,
                         msg=repr(traceback.format_exc()))

# import module snippets
from ansible.module_utils.basic import *  # noqa
from ansible.module_utils.openstack import *  # noqa
if __name__ == '__main__':
    main()
