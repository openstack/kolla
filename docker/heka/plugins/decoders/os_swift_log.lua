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
--
-- The code in this file was inspired by Heka's rsyslog.lua decoder plugin.
-- https://github.com/mozilla-services/heka/blob/master/sandbox/lua/decoders/rsyslog.lua

local syslog = require "syslog"
local utils = require "os_utils"

local msg = {
    Timestamp   = nil,
    Type        = 'log',
    Hostname    = read_config("hostname"),
    Payload     = nil,
    Pid         = nil,
    Severity    = nil,
    Fields      = nil
}

-- See https://github.com/openstack/swift/blob/2a8b455/swift/common/utils.py#L1423-L1424
local swift_grammar = syslog.build_rsyslog_grammar('<%PRI%>%programname%: %msg%')

function process_message ()
    local log = read_message("Payload")

    local fields = swift_grammar:match(log)
    if not fields then return -1 end

    msg.Severity = fields.pri.severity
    fields.syslogfacility = fields.pri.facility
    fields.pri = nil

    msg.Payload = fields.msg
    fields.msg = nil

    msg.Fields = fields
    return utils.safe_inject_message(msg)
end
