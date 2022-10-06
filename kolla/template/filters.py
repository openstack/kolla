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

from jinja2 import pass_context
from jinja2 import Undefined


@pass_context
def customizable(context, val_list, call_type):
    # NOTE(mgoddard): Don't try to customise undefined values. There are cases
    # where this might happen, for example using a generic template overrides
    # file for building multiple image install types and/or distros, where
    # variables are not defined in every case.
    if isinstance(val_list, Undefined):
        return val_list
    name = context['image_name'].replace("-", "_") + "_" + call_type + "_"
    if name + "override" in context:
        return context[name + "override"]
    if name + "append" in context:
        val_list.extend(context[name + "append"])
    if name + "remove" in context:
        for removal in context[name + "remove"]:
            if removal in val_list:
                val_list.remove(removal)
    return val_list
