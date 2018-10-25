import pandas as pd
import sys
import datetime
import subprocess as sp
import re
import os
import random
import requests
import json
import time

def check_delete_file(f_name):
    # When creating new files
    header = "Timestamp,Messages_per_sec,Latency, Message Transfer Rate\n"

    if os.access(f_name, os.R_OK):
        os.remove(f_name)

    write_to_file(header, f_name)

def read_dir(directory):
    df_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            print("Choosen file_name: %s" %filename)
            f_name = os.path.join(directory, filename)
            df_data.append(read_file(f_name))
    return df_data

def read_file(f_name):

    df = pd.read_csv(f_name, parse_dates=True)

    # This removes same signal strengths of the same mac within that specific second
    df = df.drop_duplicates(keep='first')

    df['time'] = pd.to_datetime(df['time'], format='%Y/%m/%d %H:%M:%S')

    # Look at it closer
    #start_time = datetime.datetime(2016,8, 20, 9, 20)
    #end_time = datetime.datetime(2016,8, 20, 10, 45)
    #mask = (df['time'] > start_time) & (df['time'] <= end_time)
    #df = df.loc[mask]

    df = df.set_index('time')

    return df

def read_file_randomly(f_name):

    n = sum(1 for line in open(f_name)) - 1 #number of records in file (excludes header)
    s = 500 #desired sample size
    skip = sorted(random.sample(range(1,n+1),n-s)) #the 0-indexed header will not be included in the skip list
    df = pd.read_csv(f_name, skiprows=skip)

    df = df.drop_duplicates(keep='first')

    df['time'] = pd.to_datetime(df['time'], format='%Y/%m/%d %H:%M:%S')

    df = df.set_index('time')

    return df

def post_request(url,json_data):
  REST_API_IPS = os.environ["REST_API_IPS"]
  REST_API_PORT = os.environ["REST_API_PORT"]

  IPS = REST_API_IPS.split(",")
  DEST_IP = random.choice(IPS)

  sent = False
  while (sent == False):
    try:
      r = requests.post("http://"+str(DEST_IP)+":"+str(REST_API_PORT)+"/"+url, data=json_data)
    except requests.exceptions.RequestException as e:
      print("Error caused: %s. Trying again after few seconds..." % str(e))
      time.sleep(2)
      sent = False
    else:
      #print("Successfully sent! Code: %s. Reason: %s. Elapsed time: %s Length: %s" %(str(r.status_code),str(r.reason),str(r.elapsed.total_seconds()),str(len((json_data).encode('utf-8'))*8)))
      sent = True
      return r.elapsed.total_seconds()

def send_data(url, stream_dict):

  json_data = json.dumps(stream_dict)
  headers = {'Content-Type': 'application/json'}
  #print(json_data)

  elapsed_time = post_request(url, json_data)
  return elapsed_time

def write_to_file(stats, f_name):
    """
    if not os.path.exists(f_name):
        os.mkdir(f_name)
    """
    csv = open(f_name, "a")
    csv.write(stats)
