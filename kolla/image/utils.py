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

from enum import Enum
from kolla.common import utils  # noqa


class Status(Enum):
    CONNECTION_ERROR = 'connection_error'
    PUSH_ERROR = 'push_error'
    ERROR = 'error'
    PARENT_ERROR = 'parent_error'
    BUILT = 'built'
    BUILDING = 'building'
    UNMATCHED = 'unmatched'
    MATCHED = 'matched'
    UNPROCESSED = 'unprocessed'
    SKIPPED = 'skipped'
    UNBUILDABLE = 'unbuildable'


# All error status constants.
STATUS_ERRORS = (Status.CONNECTION_ERROR, Status.PUSH_ERROR,
                 Status.ERROR, Status.PARENT_ERROR)

LOG = utils.make_a_logger()
