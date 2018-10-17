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
from random import randint,choice
import math
from pytz import timezone


def main():

    fmt = '%Y-%m-%d %H:%M'
    eastern = timezone('US/Eastern')
    stats_interval = 10 # How frequent you want to take stats (usually 30)

    #directory = "/usr/src/send_data/" # Uncomment this line when deploying it as Docker image

    # Unblock the following 3 lines when testing the code in-house
    directory = "/home/ubuntu/iot_app_ams/sensor/"
    os.environ["REST_API_IP"] = "192.168.200.11"
    os.environ["REST_API_PORT"] = "6969"


    stats_file = directory+"stats.csv" # file to hold stats
    check_delete_file(stats_file) # Remove old file and recreate it

    df_data = read_dir(directory+"sorted_data/")

    # Hold all the msg transfer rates. Then, take average and send it to stats.csv (Depracated)
    transfer_rates = []
    latencies = []

    msg_counter = 0 # counts number of msges sent

    # Track time_stamp. Need this to compare inside loop whether we passed 30 secs or not
    start_loop = time.time()
    while 1:
        for df in df_data:
            for index, row in df.iterrows():
                stream_dict = {}
                stream_dict['time_stamp'] = str(index.strftime("%Y-%m-%d %H:%M:%S"))
                stream_dict['mac'] = str(row['mac'])
                stream_dict['strength'] = str(row['strength'])
                stream_dict['onion'] = str(row['onion'])

                length = (len(str(stream_dict).encode('utf-8')))*8
                elapsed = send_data("data",stream_dict)

                curr_transfer_rate = length/elapsed
                transfer_rates.append(curr_transfer_rate)
                latencies.append(elapsed)

                end_loop = time.time()
                duration = end_loop - start_loop
                # Record every x seconds
                if int(duration) >= stats_interval:

                    avg_transfer_rate = sum(transfer_rates)/float(len(transfer_rates)) # ALG did not like this
                    msg_transfer_rate = str(math.ceil(avg_transfer_rate))              # ALG did not like this

                    avg_latency = sum(latencies)/float(len(latencies))
                    msg_latency = str(round(avg_latency,4))                                 # ALG prefers this
                    msg_per_sec = str(math.ceil((msg_counter/duration)))                       # ALG prefers this

                    # Timestamp for entering into csv
                    time_stamp = datetime.datetime.now(eastern).strftime(fmt)
                    stats = time_stamp+","+msg_per_sec+","+msg_latency+","+msg_transfer_rate+"\n"

                    write_to_file(stats, stats_file)

                    transfer_rates = [] # Reset/empty the list
                    latencies = [] # Reset/empty the list

                    start_loop = time.time() # Reset the start_time

                    msg_counter = 0

                else:
                    msg_counter += 1


    sys.exit()

if __name__=="__main__":
  main()
