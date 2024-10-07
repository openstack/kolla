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

from hacking import core

mutable_default_args = re.compile(r"^\s*def .+\((.+=\{\}|.+=\[\])")

# D703: Found use of _() without explicit import of _!

UNDERSCORE_IMPORT_FILES = []

string_translation = re.compile(r"[^_]*_\(\s*('|\")")
translated_log = re.compile(
    r"(.)*LOG\.(audit|error|info|warn|warning|critical|exception)"
    r"\(\s*_\(\s*('|\")")
underscore_import_check = re.compile(r"(.)*import _(.)*")
# We need this for cases where they have created their own _ function.
custom_underscore_check = re.compile(r"(.)*_\s*=\s*(.)*")


@core.flake8ext
def check_explicit_underscore_import(logical_line, filename):
    """Check for explicit import of the _ function

    We need to ensure that any files that are using the _() function
    to translate logs are explicitly importing the _ function.  We
    can't trust unit test to catch whether the import has been
    added so we need to check for it here.

    """

    # Build a list of the files that have _ imported.  No further
    # checking needed once it is found.
    if filename in UNDERSCORE_IMPORT_FILES:
        pass
    elif (underscore_import_check.match(logical_line) or
          custom_underscore_check.match(logical_line)):
        UNDERSCORE_IMPORT_FILES.append(filename)
    elif (translated_log.match(logical_line) or
          string_translation.match(logical_line)):
        yield (0, "D703: Found use of _() without explicit import of _!")


@core.flake8ext
def no_log_warn(logical_line):
    """Disallow 'LOG.warn('

    Deprecated LOG.warn(), instead use LOG.warning
    https://bugs.launchpad.net/senlin/+bug/1508442
    K302
    """

    msg = "K302: LOG.warn is deprecated, please use LOG.warning!"
    if "LOG.warn(" in logical_line:
        yield (0, msg)


@core.flake8ext
def no_mutable_default_args(logical_line):
    msg = "K301: Method's default argument shouldn't be mutable!"
    if mutable_default_args.match(logical_line):
        yield (0, msg)
