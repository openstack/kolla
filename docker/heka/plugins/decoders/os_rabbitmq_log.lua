-- Copyright 2015-2016 Mirantis, Inc.
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
local dt     = require "date_time"
local l      = require 'lpeg'
l.locale(l)

local patt   = require 'os_patterns'
local utils  = require 'os_utils'

local msg = {
    Timestamp   = nil,
    Type        = 'log',
    Hostname    = nil,
    Payload     = nil,
    Pid         = nil,
    Fields      = nil,
    Severity    = nil,
}

-- RabbitMQ message logs are formatted like this:
--   =ERROR REPORT==== 2-Jan-2015::09:17:22 ===
--   Blabla
--   Blabla
--
local message   = l.Cg(patt.Message / utils.chomp, "Message")
-- The token before 'REPORT' isn't standardized so it can be a valid severity
-- level as 'INFO' or 'ERROR' but also 'CRASH' or 'SUPERVISOR'.
local severity  = l.Cg(l.R"AZ"^1, "SeverityLabel")
local day = l.R"13" * l.R"09" + l.R"19"
local datetime = l.Cg(day, "day") * patt.dash * dt.date_mabbr * patt.dash * dt.date_fullyear *
                 "::" * dt.rfc3339_partial_time
local timestamp = l.Cg(l.Ct(datetime)/ dt.time_to_ns, "Timestamp")

local grammar = l.Ct("=" * severity * " REPORT==== " * timestamp * " ===" * l.P'\n' * message)

function process_message ()
    local log = read_message("Payload")

    local m = grammar:match(log)
    if not m then
        return -1
    end

    msg.Timestamp = m.Timestamp
    msg.Payload = m.Message
    msg.Logger = read_message("Logger")

    if utils.label_to_severity_map[m.SeverityLabel] then
        msg.Severity = utils.label_to_severity_map[m.SeverityLabel]
    elseif m.SeverityLabel == 'CRASH' then
        msg.Severity = 2 -- CRITICAL
    else
        msg.Severity = 5 -- NOTICE
    end

    msg.Fields = {}
    msg.Fields.severity_label = utils.severity_to_label_map[msg.Severity]
    msg.Fields.programname = 'rabbitmq'

    return utils.safe_inject_message(msg)
end
