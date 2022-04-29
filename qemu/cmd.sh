#!/bin/bash

process_id=`/bin/ps -fu $USER| grep "qemu-system-x86_64" | grep -v "grep" | awk '{print $2}'`
echo "PID for qemu instance: $process_id"
kill -n 40 $process_id
echo "Trace-start signal sent"