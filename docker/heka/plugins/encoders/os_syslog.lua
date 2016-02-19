-- Copyright 2016 Mirantis, Inc.
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
require "string"

local interpolate = require "msg_interpolate"
local utils = require "os_utils"

local header_template = "<%{Severity}>%{%FT%TZ} %{Hostname} %{programname}[%{Pid}]:"

function process_message()
    local timestamp = read_message("Timestamp") / 1e9
    local header = interpolate.interpolate_from_msg(header_template, timestamp)
    local payload = string.format("%s %s\n", header, read_message("Payload"))
    return utils.safe_inject_payload("txt", "", payload)
end
