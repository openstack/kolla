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
require "table"
local l      = require 'lpeg'
l.locale(l)

local patt = require 'os_patterns'
local utils = require 'os_utils'

local msg = {
    Timestamp   = nil,
    Type        = 'log',
    Hostname    = nil,
    Payload     = nil,
    Pid         = nil,
    Fields      = nil,
    Severity    = nil,
}

-- traceback_lines is a reference to a table used to accumulate lines of
-- a Traceback. traceback_key represent the key of the Traceback lines
-- being accumulated in traceback_lines. This is used to know when to
-- stop accumulating and inject the Heka message.
local traceback_key = nil
local traceback_lines = nil

function prepare_message (service, timestamp, pid, severity_label,
        python_module, programname, payload)
    msg.Logger = 'openstack.' .. service
    msg.Timestamp = timestamp
    msg.Payload = payload
    msg.Pid = pid
    msg.Severity = utils.label_to_severity_map[severity_label] or 7
    msg.Fields = {}
    msg.Fields.severity_label = severity_label
    msg.Fields.python_module = python_module
    msg.Fields.programname = programname
    msg.Payload = payload
end

-- OpenStack log messages are of this form:
-- 2015-11-30 08:38:59.306 3434 INFO oslo_service.periodic_task [-] Blabla...
--
-- [-] is the "request" part, it can take multiple forms.

function process_message ()

    -- Logger is of form "<service>_<program>" (e.g. "nova_nova-api",
    -- "neutron_l3-agent").
    local logger = read_message("Logger")
    local service, program = string.match(logger, '([^_]+)_(.+)')

    local log = read_message("Payload")
    local m

    m = patt.openstack:match(log)
    if not m then
        return -1, string.format("Failed to parse %s log: %s", logger, string.sub(log, 1, 64))
    end

    local key = {
        Timestamp     = m.Timestamp,
        Pid           = m.Pid,
        SeverityLabel = m.SeverityLabel,
        PythonModule  = m.PythonModule,
        service       = service,
        program       = program,
    }

    if traceback_key ~= nil then
        -- If traceback_key is not nil then it means we've started accumulated
        -- lines of a Python traceback. We keep accumulating the traceback
        -- lines util we get a different log key.
        if utils.table_equal(traceback_key, key) then
            table.insert(traceback_lines, m.Message)
            return 0
        else
            prepare_message(traceback_key.service, traceback_key.Timestamp,
                traceback_key.Pid, traceback_key.SeverityLabel,
                traceback_key.PythonModule, traceback_key.program,
                table.concat(traceback_lines, ''))
            traceback_key = nil
            traceback_lines = nil
            -- Ignore safe_inject_message status code here to still get a
            -- chance to inject the current log message.
            utils.safe_inject_message(msg)
        end
    end

    if patt.traceback:match(m.Message) then
        -- Python traceback detected, begin accumulating the lines making
        -- up the traceback.
        traceback_key = key
        traceback_lines = {}
        table.insert(traceback_lines, m.Message)
        return 0
    end

    prepare_message(service, m.Timestamp, m.Pid, m.SeverityLabel, m.PythonModule,
        program, m.Message)

    m = patt.openstack_request_context:match(msg.Payload)
    if m then
        msg.Fields.request_id = m.RequestId
        if m.UserId then
          msg.Fields.user_id = m.UserId
        end
        if m.TenantId then
          msg.Fields.tenant_id = m.TenantId
        end
    end

    m = patt.openstack_http:match(msg.Payload)
    if m then
        msg.Fields.http_method = m.http_method
        msg.Fields.http_status = m.http_status
        msg.Fields.http_url = m.http_url
        msg.Fields.http_version = m.http_version
        msg.Fields.http_response_size = m.http_response_size
        msg.Fields.http_response_time = m.http_response_time
        m = patt.ip_address:match(msg.Payload)
        if m then
            msg.Fields.http_client_ip_address = m.ip_address
        end
    end

    return utils.safe_inject_message(msg)
end
