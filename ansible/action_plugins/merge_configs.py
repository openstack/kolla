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

from ConfigParser import ConfigParser
from cStringIO import StringIO
import os

from ansible.runner.return_data import ReturnData
from ansible import utils
from ansible.utils import template


class ActionModule(object):

    TRANSFERS_FILES = True

    def __init__(self, runner):
        self.runner = runner

    def read_config(self, source, inject, config):
        # Only use config if present
        if os.access(source, os.R_OK):
            # template the source data locally & get ready to transfer
            resultant = template.template_from_file(self.runner.basedir,
                                                    source, inject)

            # Read in new results and merge this with the existing config
            fakefile = StringIO(resultant)
            config.readfp(fakefile)
            fakefile.close()

    def run(self, conn, tmp, module_name, module_args, inject,
            complex_args=None, **kwargs):
        args = {}
        if complex_args:
            args.update(complex_args)
        args.update(utils.parse_kv(module_args))

        dest = args.get('dest')
        extra_vars = args.get('vars')
        sources = args.get('sources')

        if extra_vars:
            # Extend 'inject' args used in templating
            if isinstance(extra_vars, dict):
                inject.update(extra_vars)
            else:
                inject.update(utils.parse_kv(extra_vars))

        # Catch the case where sources is a str()
        if not isinstance(sources, list):
            sources = [sources]

        config = ConfigParser()

        for source in sources:
            # template the source string
            source = template.template(self.runner.basedir, source, inject)

            try:
                self.read_config(source, inject, config)
            except Exception as e:
                return ReturnData(conn=conn, comm_ok=False,
                                  result={'failed': True, 'msg': str(e)})

        # Dump configparser to string via an emulated file
        fakefile = StringIO()
        config.write(fakefile)
        # Template the file to fill out any variables
        content = template.template(self.runner.basedir, fakefile.getvalue(),
                                    inject)
        fakefile.close()

        # Ship this content over to a new file for use with the copy module
        xfered = self.runner._transfer_str(conn, tmp, 'source', content)

        copy_module_args = dict(
            src=xfered,
            dest=dest,
            original_basename=os.path.basename(source),
            follow=True,
        )
        return self.runner._execute_module(conn, tmp, 'copy', '',
                                           inject=inject,
                                           complex_args=copy_module_args)
