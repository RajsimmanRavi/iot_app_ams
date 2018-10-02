import re
import os
import sys
import json
import time
import base64
import socket
from datetime import datetime
import subprocess as sp
from util import *
from random import choice

import requests

def post_request(json_data):
  REST_API_IP = os.environ["REST_API_IP"]
  REST_API_PORT = os.environ["REST_API_PORT"]

  sent = False
  while (sent == False):
    try:
      r = requests.post("http://"+str(REST_API_IP)+":"+str(REST_API_PORT)+"/data", data=json_data)
    except requests.exceptions.RequestException as e:
      print("Error caused: %s. Trying again..." % str(e))
      sent = False
    else:
      print("Successfully sent! Code: %s. Reason: %s" %(str(r.status_code),str(r.reason)))
      sent = True

def send_data(stream_dict):

  json_data = json.dumps(stream_dict)
  headers = {'Content-Type': 'application/json'}
  print(json_data)

  post_request(json_data)

def main():

    directory = "/usr/src/send_data/sorted_data/" # Uncomment this line when deploying it as Docker image

    """
    # Unblock the following 3 lines when testing the code in-house
    directory = "/home/ubuntu/iot_app_cascon/sensor/sorted_data/"
    os.environ["REST_API_IP"] = "10.2.1.13"
    os.environ["REST_API_PORT"] = "6969"
    """
    while 1:
        df = read_file_randomly(directory+choice(os.listdir(directory)))

        for index, row in df.iterrows():
            stream_dict = {}
            stream_dict['time_stamp'] = str(index.strftime("%Y-%m-%d %H:%M:%S"))
            stream_dict['mac'] = str(row['mac'])
            stream_dict['strength'] = str(row['strength'])
            stream_dict['onion'] = str(row['onion'])

            length = (sys.getsizeof(stream_dict))*8
            start = time.time()
            send_data(stream_dict)
            end = time.time()

            elapsed = end - start
            transfer_rate = length/elapsed
            print("Length: %s, Time elapsed: %s, transfer_rate: %s" %(length, elapsed, str(transfer_rate)))
    sys.exit()

if __name__=="__main__":
  main()
