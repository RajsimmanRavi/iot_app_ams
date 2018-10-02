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
from random import randint

import requests

def post_request(url,json_data):
  REST_API_IP = os.environ["REST_API_IP"]
  REST_API_PORT = os.environ["REST_API_PORT"]

  sent = False
  while (sent == False):
    try:
      r = requests.post("http://"+str(REST_API_IP)+":"+str(REST_API_PORT)+"/"+url, data=json_data)
    except requests.exceptions.RequestException as e:
      print("Error caused: %s. Trying again after few seconds..." % str(e))
      time.sleep(2)
      sent = False
    else:
      print("Successfully sent! Code: %s. Reason: %s" %(str(r.status_code),str(r.reason)))
      sent = True

def send_data(url, stream_dict):

  json_data = json.dumps(stream_dict)
  headers = {'Content-Type': 'application/json'}
  print(json_data)

  post_request(url, json_data)

def main():

    directory = "/usr/src/send_data/sorted_data/" # Uncomment this line when deploying it as Docker image

    """
    # Unblock the following 3 lines when testing the code in-house
    directory = "/home/ubuntu/iot_app_cascon/sensor/sorted_data/"
    os.environ["REST_API_IP"] = "10.2.1.13"
    os.environ["REST_API_PORT"] = "6969"
    """

    df_data = read_dir(directory)

    while 1:
        for df in df_data:
            counter = 1
            for index, row in df.iterrows():
                stream_dict = {}
                stats_dict = {}
                stream_dict['time_stamp'] = str(index.strftime("%Y-%m-%d %H:%M:%S"))
                stream_dict['mac'] = str(row['mac'])
                stream_dict['strength'] = str(row['strength'])
                stream_dict['onion'] = str(row['onion'])

                length = (sys.getsizeof(stream_dict))*8
                start = time.time()
                send_data("data",stream_dict)
                end = time.time()

                elapsed = end - start
                transfer_rate = length/elapsed

                stats_dict['time_stamp'] = stream_dict['time_stamp'] # Same as the sent msg
                stats_dict['transfer_rate'] = str(transfer_rate)
                stats_dict['latency'] = str(elapsed)
                stats_dict['length'] = str(length)
                #send_data("stats",stats_dict)

                hostname = str(os.system("hostname"))
                print(hostname)
                if not os.path.exists(directory+hostname):
                    os.mkdir(directory+hostname)

                f_name = directory+hostname+"/stats.csv"

                stats = stats_dict['time_stamp']+","+stats_dict['transfer_rate']+","+stats_dict['latency']+","+stats_dict['length']+"\n"

                csv = open(f_name, "a")
                csv.write(stats)

                counter += 1

                if counter % 100 == 0:
                    time.sleep(5)
    sys.exit()

if __name__=="__main__":
  main()
