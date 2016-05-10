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

import json
import sys
import traceback

from keystoneclient import exceptions
from keystoneclient.v2_0 import client

os_token = sys.argv[1]
password = sys.argv[2]
project = sys.argv[3]
role = sys.argv[4]
admin_url = sys.argv[5]
internal_url = sys.argv[6]
public_url = sys.argv[7]
region = sys.argv[8]
os_url = sys.argv[9]

changed = False
failed = False

try:
    ks = client.Client(token=os_token, endpoint=os_url)

    services = [s for s in ks.services.list() if s.type == "identity"]
    if not services:
        service = ks.services.create(
            name="keystone",
            service_type="identity",
            description="OpenStack Identity")
        changed = True
    else:
        service = services[0]

    endpoints = [e for e in ks.endpoints.list() if e.service_id == service.id]
    if not endpoints:
        ks.endpoints.create(region, service.id, public_url,
                            adminurl=admin_url, internalurl=internal_url)
        changed = True

    try:
        tenant = ks.tenants.create("admin", description="Admin Project")
    except exceptions.Conflict as e:
        tenant = [t for t in ks.tenants.list() if t.name == "admin"][0]
    else:
        changed = True

    try:
        user = ks.users.create("admin", password=password)
    except exceptions.Conflict as e:
        user = [u for u in ks.users.list() if u.username == "admin"][0]
    else:
        changed = True

    try:
        role = ks.roles.create("admin")
    except exceptions.Conflict as e:
        role = [r for r in ks.roles.list() if r.name == "admin"][0]
    else:
        changed = True

    if not ks.roles.roles_for_user(user.id, tenant=tenant.id):
        changed = True
        ks.roles.add_user_role(role=role, user=user.id, tenant=tenant.id)

except Exception as e:
    result = {
        'failed': True,
        'changed': True,
        'msg': traceback.format_exc(),
    }
else:
    result = {
        'failed': False,
        'changed': changed,
        'msg': 'OK'
    }

print(json.dumps(result))
