import datetime
import time
import zoneinfo
import json

import pandas as pd
from kafka import KafkaProducer

if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers="localhost:29091,localhost:29092,localhost:29093",
    )

    my_tz = zoneinfo.ZoneInfo("Asia/Ho_Chi_minh")

    data = pd.read_csv("cleaner_weather_data.csv")
    sensor_data = data[data["StationCode"] == 101]
    sensor_data = sensor_data.astype({"StationCode": int})

    try:
        while True:
            for row in sensor_data.itertuples(index=False):
                current_time = datetime.datetime.now(my_tz).isoformat()

                new_row = row._asdict()
                new_row["PM2.5"] = new_row.pop("_6")
                new_row["SendTime"] = current_time
                producer.send("foobar", bytes(json.dumps(new_row), "utf-8"))

                print(f"Send message : {json.dumps(new_row)}")
                time.sleep(10)

    except KeyboardInterrupt:
        producer.close()
