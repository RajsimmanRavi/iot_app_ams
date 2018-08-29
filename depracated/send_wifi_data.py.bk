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

def read_files(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith(".pcap"):
            sniff(offline=os.path.join(directory,file_name),prn=send_pkt, store=0)

def get_mac(pkt):
  if pkt.haslayer(Dot11):
      mac = pkt[Dot11].addr2
      return mac

# Fetches stats and sends it to appropriate endpoint in JSON format (kinda)
def send_pkt(pkt):

  UDP_IP = os.environ["KAFKA_IP"]
  UDP_PORT = os.environ["KAFKA_PORT"]

  mac = get_mac(pkt)

  if mac:
      # build json object
      data = {}
      data['mac'] = mac

      print(str(data))
      json_data = json.dumps(data)

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

def main():

  #os.environ["KAFKA_IP"] = "10.2.1.11"
  #os.environ["KAFKA_PORT"] = "9092"
  directory = "/usr/src/send_data/onion233E/"
  #directory = "/home/ubuntu/iot_app_cascon/sensor/onion233E/"

  while 1:
    timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    print("Starting data collection and transmission for: "+str(timestamp))
    sys.stdout.flush()

    read_files(directory)

    sys.stdout.flush()
    time.sleep(5)

  sys.exit()

if __name__=="__main__":
  main()

