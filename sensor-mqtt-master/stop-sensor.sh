#!/bin/bash

if [[ ! -e "/tmp/sensor.pid" ]]; then
    echo "Process isn't running"
    exit 1
fi

PID=`cat /tmp/sensor.pid`
kill $PID
