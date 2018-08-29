import pandas as pd
import sys
import datetime
import subprocess as sp
import re
import os

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

