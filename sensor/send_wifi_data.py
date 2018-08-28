import re
import os
import sys
import json
import time
import base64
import socket
from datetime import datetime
import subprocess as sp
from scapy.all import *
from kafka import KafkaProducer
from util import *

# Fetches stats and sends it to appropriate endpoint in JSON format (kinda)
def send_data(stream_dict):

  UDP_IP = os.environ["KAFKA_IP"]
  UDP_PORT = os.environ["KAFKA_PORT"]

  json_data = json.dumps(stream_dict)

  print(json_data)

  """
  # send data to Kafka consumer
  try:
    kafka_server = UDP_IP+":"+str(UDP_PORT)
    producer = KafkaProducer(bootstrap_servers=kafka_server)
    producer.send('stats', json_data.encode('utf8'))
    producer.flush()
    producer.close()
  except Exception as e:
    print("Error occurred during data transmission process!")
    print(str(e))
    pass
  else:
    print("Successfully transmitted data!")
  """

def main():

  os.environ["KAFKA_IP"] = "10.2.1.11"
  os.environ["KAFKA_PORT"] = "9092"
  #directory = "/usr/src/sorted_data/"
  directory = "/home/ubuntu/iot_app_cascon/sensor/sorted_data/"

  df_data = read_dir(directory)

  for df in df_data:
      for index, row in df.iterrows():
          stream_dict = {}
          stream_dict['time_stamp'] = index.strftime("%Y-%m-%d %H:%M:%S")
          stream_dict['mac'] = row['mac']
          stream_dict['strength'] = row['strength']
          send_data(stream_dict)
  """
  while 1:
    timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    print("Starting data collection and transmission for: "+str(timestamp))
    sys.stdout.flush()

    util.read_file(directory)

    sys.stdout.flush()
    time.sleep(5)

  sys.exit()
  """
if __name__=="__main__":
  main()

