import pandas as pd
import sys
import datetime
import subprocess as sp
import re
import os

def mac_lookup(command):
    try:
        process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
        try:
            output, err = process.communicate(timeout=180) # Python3
        except:
            output, err = process.communicate() # Python2.7
    except Exception as e:
        print("Caught error while running command: %s...Exiting!" % command)
        print(str(e))
        sys.exit(1)

    if output:
        output = output.decode("utf-8")
        output = re.split(r'\t+',output)[1]
        return output.rstrip()

def parse_mac(mac):
    prefix = mac.replace(":","")[0:6]
    cmd = "grep -i "+prefix+" oui.txt"
    lookup = mac_lookup(cmd)
    #print("%s:%s" %(mac,lookup))
    return lookup
    #print(send_data)
    #return send_data

def filter_common_macs(df,comm_macs_file):

    comm_macs = list(line.strip() for line in open(comm_macs_file))
    df = df[df['mac'].isin(comm_macs)]

    return df

def read_dir(directory):
    df_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
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

def get_common_macs_for_tracking(df_data,min_samples=0):

    name_list = []
    for df in df_data:

        grouped_df = df.groupby('mac')

        names = []
        for name, group in grouped_df:
            group = group.resample('1T').mean().interpolate()
            group = group.strength.astype(int)
            if len(group) >= min_samples:
                names.append(name)
        name_list.append(names)

    common_macs = list(set(name_list[0]).intersection(name_list[1]))
    #print(len(common_macs))
    return common_macs
