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

import ConfigParser
import inspect
import os
from six import StringIO

from ansible.plugins import action


class ActionModule(action.ActionBase):

    TRANSFERS_FILES = True

    def read_config(self, source, config):
        # Only use config if present
        if os.access(source, os.R_OK):
            with open(source, 'r') as f:
                template_data = f.read()
            result = self._templar.template(template_data)
            fakefile = StringIO(result)
            config.readfp(fakefile)
            fakefile.close()

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()
        result = super(ActionModule, self).run(tmp, task_vars)

        # NOTE(jeffrey4l): Ansible 2.1 add a remote_user param to the
        # _make_tmp_path function.  inspect the number of the args here. In
        # this way, ansible 2.0 and ansible 2.1 are both supported
        make_tmp_path_args = inspect.getargspec(self._make_tmp_path)[0]
        if not tmp and len(make_tmp_path_args) == 1:
            tmp = self._make_tmp_path()
        if not tmp and len(make_tmp_path_args) == 2:
            remote_user = (task_vars.get('ansible_ssh_user')
                           or self._play_context.remote_user)
            tmp = self._make_tmp_path(remote_user)

        sources = self._task.args.get('sources', None)
        extra_vars = self._task.args.get('vars', list())

        if not isinstance(sources, list):
            sources = [sources]

        temp_vars = task_vars.copy()
        temp_vars.update(extra_vars)

        config = ConfigParser.ConfigParser()
        old_vars = self._templar._available_variables
        self._templar.set_available_variables(temp_vars)

        for source in sources:
            self.read_config(source, config)

        self._templar.set_available_variables(old_vars)
        # Dump configparser to string via an emulated file

        fakefile = StringIO()
        config.write(fakefile)

        remote_path = self._connection._shell.join_path(tmp, 'src')
        xfered = self._transfer_data(remote_path, fakefile.getvalue())
        fakefile.close()

        new_module_args = self._task.args.copy()
        new_module_args.pop('vars', None)
        new_module_args.pop('sources', None)

        new_module_args.update(
            dict(
                src=xfered
            )
        )

        result.update(self._execute_module(module_name='copy',
                                           module_args=new_module_args,
                                           task_vars=task_vars,
                                           tmp=tmp))
        return result
