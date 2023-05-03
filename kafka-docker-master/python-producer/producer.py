from kafka import KafkaProducer

import time

import asyncio

import kafka

def print_result(result):
  print(result)



if __name__ == "__main__":
  producer = KafkaProducer(bootstrap_servers="localhost:29091,localhost:29092,localhost:29093", 
                           acks='all', retries=3, max_in_flight_requests_per_connection=1)

  for i in range(10):
    result = producer.send("test-topic", (i + 64).to_bytes(1, 'big'))
    result.add_callback(print_result)
    time.sleep(3)