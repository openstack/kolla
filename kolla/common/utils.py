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

import logging
import os
import subprocess  # nosec
import sys


def make_a_logger(conf=None, image_name=None):
    if image_name:
        log = logging.getLogger(".".join([__name__, image_name]))
    else:
        log = logging.getLogger(__name__)
    if not log.handlers:
        if conf is None or not conf.logs_dir or not image_name:
            handler = logging.StreamHandler(sys.stderr)
            log.propagate = False
        else:
            filename = os.path.join(conf.logs_dir, "%s.log" % image_name)
            handler = logging.FileHandler(filename, delay=True)
        handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        log.addHandler(handler)
    if conf is not None and conf.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    return log


LOG = make_a_logger()


def get_docker_squash_version():

    try:
        stdout = subprocess.check_output(  # nosec
            ['docker-squash', '--version'], stderr=subprocess.STDOUT)
        return stdout.split()[0]
    except OSError as ex:
        if ex.errno == 2:
            LOG.error(('"docker-squash" command is not found.'
                       ' try to install it by "pip install docker-squash"'))
        raise


def squash(old_image, new_image,
           from_layer=None,
           cleanup=False,
           tmp_dir=None):

    cmds = ['docker-squash', '--tag', new_image, old_image]
    if cleanup:
        cmds += ['--cleanup']
    if from_layer:
        cmds += ['--from-layer', from_layer]
    if tmp_dir:
        cmds += ['--tmp-dir', tmp_dir]
    try:
        subprocess.check_output(cmds, stderr=subprocess.STDOUT)  # nosec
    except subprocess.CalledProcessError as ex:
        LOG.exception('Get error during squashing image: %s',
                      ex.stdout)
        raise
