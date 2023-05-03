#!/bin/bash

if [[ -f "/tmp/sensor.id" ]]; then
    echo "Process is already running"
    exit 1
fi

source ".venv/bin/activate"

python3 "sensor_mqtt.py" &
exit