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

import traceback

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

        cloud = shade.OperatorCloud(**module.params)

        for _project in cloud.search_projects():
            if _project.name == project_name:
                project = _project

        for _role in cloud.search_roles():
            if _role.name == role_name:
                role = _role

        for _user in cloud.search_users():
            if _user.name == user_name:
                user = _user

        if not project:
            changed = True
            project = cloud.create_project(project_name,
                                           domain_id='default')

        if not role:
            changed = True
            role = cloud.create_role(role_name)

        if not user:
            changed = True
            user = cloud.create_user(user_name,
                                     password=password,
                                     default_project=project,
                                     domain_id='default')
            cloud.grant_role(role,
                             user=user,
                             project=project)

        module.exit_json(changed=changed)
    except Exception:
        module.exit_json(failed=True, changed=True,
                         msg=repr(traceback.format_exc()))

# import module snippets
from ansible.module_utils.basic import *  # noqa
from ansible.module_utils.openstack import *  # noqa
if __name__ == '__main__':
    main()
