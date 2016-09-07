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

import re


mutable_default_args = re.compile(r"^\s*def .+\((.+=\{\}|.+=\[\])")


def no_log_warn(logical_line):
    """Disallow 'LOG.warn('

    Deprecated LOG.warn(), instead use LOG.warning
    https://bugs.launchpad.net/senlin/+bug/1508442
    N352
    """

    msg = ("N352: LOG.warn is deprecated, please use LOG.warning!")
    if "LOG.warn(" in logical_line:
        yield (0, msg)


def no_mutable_default_args(logical_line):
    msg = "N301: Method's default argument shouldn't be mutable!"
    if mutable_default_args.match(logical_line):
        yield (0, msg)


def factory(register):
    register(no_mutable_default_args)
    register(no_log_warn)
