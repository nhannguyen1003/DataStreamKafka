import atexit
import datetime
import json
import logging
import os
import pathlib
import signal
import sys
import time
from configparser import ConfigParser
from typing import Optional
import paho.mqtt.client as mqtt
import pandas as pd
import requests

# Global MQTT Client
mqtt_client: Optional[mqtt.Client] = None


@atexit.register
def on_exit():
    pathlib.Path("/tmp/sensor.pid").unlink()

    logger.info(f"Sensor {STATION_CODE} is shutdown")

    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


def stop_sensor(sig_num, stack_frame):
    sys.exit()


def create_mqtt_client(config: ConfigParser) -> mqtt.Client:
    broker = config.get("mqtt", "broker")
    port = config.getint("mqtt", "port")
    token = config.get("mqtt", "token")

    client = mqtt.Client("sensor")
    client.username_pw_set(token)
    client.connect(broker, port)

    client.loop_start()

    return client


if __name__ == "__main__":
    file_path = pathlib.Path(__file__).resolve().parent
    with open("/tmp/sensor.pid", "w") as pid_file:
        pid_file.write(str(os.getpid()))

    signal.signal(signal.SIGTERM, stop_sensor)
    signal.signal(signal.SIGINT, stop_sensor)

    # Reading configurations
    configs = ConfigParser()
    configs.read(file_path / "conf" / "sensor.cfg")

    STATION_CODE = configs.getint("sensor", "sensor.number")
    DELAY_TIME = configs.getint("sensor", "delay.time")
    DEBUG_LEVEL = configs.get("sensor", "debug.level")

    # Create logger
    logger = logging.getLogger("mqtt-sensor")
    logger.setLevel(DEBUG_LEVEL)

    file_handler = logging.FileHandler(file_path / "logs" / "sensor.log")
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")

    logger.addHandler(file_handler)
    file_handler.setFormatter(formatter)

    all_sensor_data = pd.read_csv(file_path / "cleaner_weather_data.csv")
    sensor_data = all_sensor_data[all_sensor_data["StationCode"] == STATION_CODE]
    sensor_data = sensor_data.astype({"StationCode": int})

    logger.info(f"Sensor {STATION_CODE} is ready.")

    if configs.has_section("mqtt"):
        MQTT_TOPIC = configs.get("mqtt", "topic")
        mqtt_client = create_mqtt_client(configs)
    else:
        hostname = configs.get("http", "hostname")
        token = configs.get("http", "token")

        HTTP_URL = f"http://{hostname}/api/v1/{token}/telemetry"

    # my_tz = zoneinfo.ZoneInfo("Asia/Ho_Chi_minh")

    # Sending data
    while True:
        for row in sensor_data.itertuples(index=False):
            current_time = datetime.datetime.now().isoformat()

            new_row = row._asdict()
            new_row["PM2.5"] = new_row.pop("_6")
            new_row["SendTime"] = current_time

            if mqtt_client:
                mqtt_client.publish(MQTT_TOPIC, json.dumps(new_row), 1)
            else:
                requests.post(
                    url=HTTP_URL,
                    data=json.dumps(new_row),
                    headers={"Content-Type": "application/json"},
                )

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(json.dumps(new_row))
            time.sleep(DELAY_TIME)
