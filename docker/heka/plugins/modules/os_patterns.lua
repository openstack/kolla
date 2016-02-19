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
local table  = require 'table'
local dt     = require "date_time"
local l      = require 'lpeg'
l.locale(l)

local tonumber = tonumber

local M = {}
setfenv(1, M) -- Remove external access to contain everything in the module

function format_uuid(t)
    return table.concat(t, '-')
end

function anywhere (patt)
  return l.P {
    patt + 1 * l.V(1)
  }
end

sp = l.space
colon = l.P":"
dash = l.P"-"
dot = l.P'.'
quote = l.P'"'

local x4digit = l.xdigit * l.xdigit * l.xdigit * l.xdigit
local uuid_dash = l.C(x4digit * x4digit * dash * x4digit * dash * x4digit * dash * x4digit * dash * x4digit * x4digit * x4digit)
local uuid_nodash = l.Ct(l.C(x4digit * x4digit) * l.C(x4digit) * l.C(x4digit) * l.C(x4digit) * l.C(x4digit * x4digit * x4digit)) / format_uuid

-- Return a UUID string in canonical format (eg with dashes)
Uuid = uuid_nodash + uuid_dash

-- Parse a datetime string and return a table with the following keys
--   year (string)
--   month (string)
--   day (string)
--   hour (string)
--   min (string)
--   sec (string)
--   sec_frac (number less than 1, can be nil)
--   offset_sign ('-' or '+', can be nil)
--   offset_hour (number, can be nil)
--   offset_min (number, can be nil)
--
-- The datetime string can be formatted as
-- 'YYYY-MM-DD( |T)HH:MM:SS(.ssssss)?(offset indicator)?'
TimestampTable = l.Ct(dt.rfc3339_full_date * (sp + l.P"T") * dt.rfc3339_partial_time * (dt.rfc3339_time_offset + dt.timezone_offset)^-1)

-- Returns the parsed datetime converted to nanosec
Timestamp = TimestampTable / dt.time_to_ns

programname   = (l.R("az", "AZ", "09") + l.P"." + dash + l.P"_")^1
Pid           = l.digit^1
SeverityLabel = l.P"CRITICAL" + l.P"ERROR" + l.P"WARNING" + l.P"INFO" + l.P"AUDIT" + l.P"DEBUG"
Message       = l.P(1)^0

-- Capture for OpenStack logs producing four values: Timestamp, Pid,
-- SeverityLabel, PythonModule and Message.
--
-- OpenStack log messages are of this form:
-- 2015-11-30 08:38:59.306 3434 INFO oslo_service.periodic_task [-] Blabla...
--
-- [-] is the "request" part, it can take multiple forms. See below.
openstack = l.Ct(l.Cg(Timestamp, "Timestamp")* sp * l.Cg(Pid, "Pid") * sp *
    l.Cg(SeverityLabel, "SeverityLabel") * sp * l.Cg(programname, "PythonModule") *
    sp * l.Cg(Message, "Message"))

-- Capture for OpenStack request context producing three values: RequestId,
-- UserId and TenantId.
--
-- Notes:
--
-- OpenStack logs include a request context, enclosed between square brackets.
-- It takes one of these forms:
--
-- [-]
-- [req-0fd2a9ba-448d-40f5-995e-33e32ac5a6ba - - - - -]
-- [req-4db318af-54c9-466d-b365-fe17fe4adeed 8206d40abcc3452d8a9c1ea629b4a8d0 112245730b1f4858ab62e3673e1ee9e2 - - -]
--
-- In the 1st case the capture produces nil.
-- In the 2nd case the capture produces one value: RequestId.
-- In the 3rd case the capture produces three values: RequestId, UserId, TenantId.
--
-- The request id  may be formatted as 'req-xxx' or 'xxx' depending on the project.
-- The user id and tenant id may not be present depending on the OpenStack release.
openstack_request_context = (l.P(1) - "[" )^0 * "[" * l.P"req-"^-1 *
    l.Ct(l.Cg(Uuid, "RequestId") * sp * ((l.Cg(Uuid, "UserId") * sp *
    l.Cg(Uuid, "TenantId")) + l.P(1)^0)) - "]"

local http_method = l.Cg(l.R"AZ"^3, "http_method")
local url = l.Cg( (1 - sp)^1, "http_url")
local http_version = l.Cg(l.digit * dot * l.digit, "http_version")

-- Pattern for the "<http_method> <http_url> HTTP/<http_version>" format found
-- found in both OpenStack and Apache log files.
-- Example : OPTIONS /example.com HTTP/1.0
http_request = http_method * sp * url * sp * l.P'HTTP/' * http_version

-- Patterns for HTTP status, HTTP response size and HTTP response time in
-- OpenLayers logs.
--
-- Notes:
-- Nova changes the default log format of eventlet.wsgi (see nova/wsgi.py) and
-- prefixes the HTTP status, response size and response time values with
-- respectively "status: ", "len: " and "time: ".
-- Other OpenStack services just rely on the default log format.
-- TODO(pasquier-s): build the LPEG grammar based on the log_format parameter
-- passed to eventlet.wsgi.server similar to what the build_rsyslog_grammar
-- function does for RSyslog.
local openstack_http_status = l.P"status: "^-1 * l.Cg(l.digit^3, "http_status")
local openstack_response_size = l.P"len: "^-1 * l.Cg(l.digit^1 / tonumber, "http_response_size")
local openstack_response_time = l.P"time: "^-1 * l.Cg(l.digit^1 * dot^0 * l.digit^0 / tonumber, "http_response_time")

-- Capture for OpenStack HTTP producing six values: http_method, http_url,
-- http_version, http_status, http_response_size and http_response_time.
openstack_http = anywhere(l.Ct(
    quote * http_request * quote * sp *
    openstack_http_status * sp * openstack_response_size * sp *
    openstack_response_time
))

-- Capture for IP addresses producing one value: ip_address.
ip_address = anywhere(l.Ct(
    l.Cg(l.digit^-3 * dot * l.digit^-3 * dot * l.digit^-3 * dot * l.digit^-3, "ip_address")
))

-- Pattern used to match the beginning of a Python Traceback.
traceback = l.P'Traceback (most recent call last):'

return M
