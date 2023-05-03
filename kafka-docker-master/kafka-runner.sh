#!/bin/bash

trap terminate SIGTERM

terminate() {
  echo "Terminating";
  /kafka_2.13-3.1.0/bin/kafka-server-stop.sh /conf/server.properties;
  /kafka_2.13-3.1.0/bin/zookeeper-server-stop.sh /conf/zookeeper.properties;

  exit;
}

/kafka_2.13-3.1.0/bin/zookeeper-server-start.sh -daemon /conf/zookeeper.properties
/kafka_2.13-3.1.0/bin/kafka-server-start.sh /conf/server.properties &

while true
do
  sleep 1
done