# Wait-for function

The usage of the wait_for function looks like the following
    $ SCRIPT_NAME LOOPS_NUMBER SLEEP_TIME ARGS

The ARGS are read and concatenated together into a single command
and the command is executed in a loop until it succeeds or reaches
the max number of attempts (LOOPS_NUMBER).

An optional FAIL_MATCH_OUTPUT variable may also be set to control
if the loop exits early if the commands stdout/stderr matches the
supplied regex string.
Examples:
    $ wait_for 30 10 ping -c 1 192.0.2.2
    $ wait_for 10 1 ls file_we_are_waiting_for
    $ wait_for 10 3 date \| grep 8
    $ FAIL_MATCH_OUTPUT=CREATE_FAILED wait_for 30 10 heat stack-show undercloud
    $ SUCCESSFUL_MATCH_OUTPUT=CREATE_COMPLETE wait_for 30 10 heat stack-show undercloud
