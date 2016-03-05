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
        password=dict(required=True, type='str'),
        project=dict(required=True, type='str'),
        role=dict(required=True, type='str'),
        user=dict(required=True, type='str')
    )
    module = AnsibleModule(argument_spec)

    try:
        password = module.params.pop('password')
        project_name = module.params.pop('project')
        role_name = module.params.pop('role')
        user_name = module.params.pop('user')

        changed = False
        project = None
        role = None
        user = None

        cloud = shade.operator_cloud(**module.params)

        for _project in cloud.keystone_client.projects.list():
            if _project.name == project_name:
                project = _project

        for _role in cloud.keystone_client.roles.list():
            if _role.name == role_name:
                role = _role

        for _user in cloud.keystone_client.users.list():
            if _user.name == user_name:
                user = _user

        if not project:
            changed = True
            project = cloud.keystone_client.projects.create(
                name=project_name, domain='default')

        if not role:
            changed = True
            role = cloud.keystone_client.roles.create(name=role_name)

        if not user:
            changed = True
            user = cloud.keystone_client.users.create(name=user_name,
                                                      password=password,
                                                      project=project)
            cloud.keystone_client.roles.grant(role=role,
                                              user=user,
                                              project=project)

        module.exit_json(changed=changed)
    except Exception as e:
        module.exit_json(failed=True, changed=True, msg=e)

# import module snippets
from ansible.module_utils.basic import *  # noqa
from ansible.module_utils.openstack import *  # noqa
if __name__ == '__main__':
    main()
