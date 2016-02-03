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
require "string"
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
    Fields      = {},
    Severity    = nil,
}

local sp    = patt.sp
local colon = patt.colon

-- mysqld logs are cranky,the date is YYMMMDD, the hours have no leading zero and the "real" severity level is enclosed by square brackets...
local mysql_grammar = l.Ct(l.digit^-6 * sp^1 *  l.digit^-2 * colon * l.digit^-2 * colon * l.digit^-2 * sp^1 * l.P"[" * l.Cg(l.R("az", "AZ")^0 / string.upper, "SeverityLabel") * l.P"]" * sp^1 * l.Cg(patt.Message, "Message"))


function process_message ()
    local log = read_message("Payload")
    local logger = read_message("Logger")

    local m = mysql_grammar:match(log)
    if not m then return -1 end

    msg.Logger = logger
    msg.Payload = m.Message
    msg.Fields.severity_label = m.SeverityLabel

    return utils.safe_inject_message(msg)
end
