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

    directory = "/usr/src/send_data/" # Uncomment this line when deploying it as Docker image

    """
    # Unblock the following 3 lines when testing the code in-house
    directory = "/home/ubuntu/iot_app_cascon/sensor/"
    os.environ["REST_API_IP"] = "10.2.1.13"
    os.environ["REST_API_PORT"] = "6969"
    """

    stats_file = directory+"stats.csv" # file to hold stats

    df_data = read_dir(directory+"sorted_data/")

    # Hold all the msg transfer rates. Then, take average and send it to stats.csv
    transfer_rates = []

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

                length = (sys.getsizeof(stream_dict))*8

                # Measure time elapsed during transfer
                start = time.time()
                send_data("data",stream_dict)
                end = time.time()

                elapsed = end - start

                curr_transfer_rate = length/elapsed
                transfer_rates.append(curr_transfer_rate)

                end_loop = time.time()

                # Record every 30 seconds
                if int(end_loop - start_loop) >= 30:

                    avg_transfer_rate = sum(transfer_rates)/float(len(transfer_rates))
                    msg_transfer_rate = str(math.ceil(avg_transfer_rate))
                    #msg_latency = str(round(elapsed,4)) Not adding anymore, depracated

                    # Timestamp for entering into csv
                    time_stamp = datetime.datetime.now(eastern).strftime(fmt)
                    stats = time_stamp+","+msg_transfer_rate+"\n"

                    check_delete_file(stats_file)
                    write_to_file(stats, stats_file)
                    #time.sleep(5)
                    transfer_rates = [] # Reset/empty the list
                    start_loop = time.time() # Reset the start_time


    sys.exit()

if __name__=="__main__":
  main()
