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
local cjson = require 'cjson'
local string = require 'string'

local patt  = require 'os_patterns'

local pairs = pairs
local inject_message = inject_message
local inject_payload = inject_payload
local read_message = read_message
local pcall = pcall

local M = {}
setfenv(1, M) -- Remove external access to contain everything in the module

severity_to_label_map = {
    [0] = 'EMERGENCY',
    [1] = 'ALERT',
    [2] = 'CRITICAL',
    [3] = 'ERROR',
    [4] = 'WARNING',
    [5] = 'NOTICE',
    [6] = 'INFO',
    [7] = 'DEBUG',
}

label_to_severity_map = {
    EMERGENCY = 0,
    ALERT = 1,
    CRITICAL = 2,
    ERROR = 3,
    WARNING = 4,
    NOTICE = 5,
    INFO= 6,
    DEBUG = 7,
}

function chomp(s)
    return string.gsub(s, "\n$", "")
end

-- Call inject_message() wrapped by pcall()
function safe_inject_message(msg)
    local ok, err_msg = pcall(inject_message, msg)
    if not ok then
        return -1, err_msg
    else
        return 0
    end
end

-- Call inject_payload() wrapped by pcall()
function safe_inject_payload(payload_type, payload_name, data)
    local ok, err_msg = pcall(inject_payload, payload_type, payload_name, data)
    if not ok then
        return -1, err_msg
    else
        return 0
    end
end

-- Shallow comparison between two tables.
-- Return true if the two tables have the same keys with identical
-- values, otherwise false.
function table_equal(t1, t2)
    -- all key-value pairs in t1 must be in t2
    for k, v in pairs(t1) do
        if t2[k] ~= v then return false end
    end
    -- there must not be other keys in t2
    for k, v in pairs(t2) do
        if t1[k] == nil then return false end
    end
    return true
end

return M
