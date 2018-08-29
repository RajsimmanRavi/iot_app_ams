import pandas as pd
import matplotlib.pyplot as plt
import sys
import datetime
from util import *

def resample_data(df,drop_dup=False):
    #print("Original: %s" %df)
    agg = df.drop(['strength'], axis=1)
    #print("After dropping strength: %s" %agg)
    
    """            
    # For validating my grouping 
    agg2 = agg.groupby(['time'])
    for name, group in agg2:
        #print(name)
        print(group)
    """

    if drop_dup:
        agg = agg.groupby(['time'])['mac'].nunique()
        #print("After grouping and dropping duplicates: %s" %agg)
    else:
        agg = agg.groupby(['time']).size()
        #print("After grouping by time: %s" %agg)
    
    
    ### Works
    agg = agg.resample('5T').sum()
    #print("After resampling into 5 mins: %s" %agg)
    #agg = agg.resample('10S').sum() # alg asked for it
    
    return agg

def trim_df(df_data):
    trimmed_data = []
    for df in df_data:
        # Look at it closer
        start_time = datetime.datetime(2016,8, 20, 9, 20)
        end_time = datetime.datetime(2016,8, 20, 10, 45)
        #end_time = datetime.datetime(2016,8, 20, 9, 45)
        mask = (df.index > start_time) & (df.index <= end_time)
        df = df.loc[mask]
        trimmed_data.append(df)
    return trimmed_data


def df_compare(df_data):
    
    fig, axes = plt.subplots(nrows=2, ncols=1)
    
    axes[0].set_title("Number of Devices Monitored (with Duplicates) for Entire Period")
    axes[0].set_ylabel("Number of Devices")
    axes[0].grid('on', which='minor', axis='x') 

    counter = 1    
    for df in df_data:
        res = resample_data(df)
        res.plot(ax=axes[0],kind='line',legend=True,label="onion"+str(counter), grid=True, style='o-')
        counter += 1
    
    trimmed_df = trim_df(df_data)
    
    axes[1].set_title("Number of Devices Monitored (without Duplicates) around 9:30 - 10:30 AM")
    axes[1].set_ylabel("Number of Devices")
    axes[1].grid('on', which='minor', axis='x' ) 
    
    counter = 1
    for df in trimmed_df:
        print("df: %s" % str(df.shape))
        print(len(df['mac'].unique()))
        
        resampled_df = resample_data(df,drop_dup=True)
        print(resampled_df)
        resampled_df.plot(ax=axes[1],kind='line',legend=True,label="onion"+str(counter), grid=True, style='o-')
        #df2.plot(ax=ax,kind='line',legend=True,label="onion233E",style='ro-')
        
        """
        print(df)
        df = df.drop(['strength'], axis=1)
        agg = df.drop_duplicates(keep='first')
        print(df) 
        rint(agg)
        df = df.groupby(['time']).size()
        agg = agg.groupby(['time']).size()

        df = df.resample('10S').sum()
        agg = agg.resample('10S').sum()
        
        print(df)
        print(agg)

        df.plot(ax=ax,kind='line',legend=True,label="onion"+str(counter)+" with duplicates", grid=True)
        agg.plot(ax=ax,kind='line',legend=True,label="onion"+str(counter), grid=True)
        """

        counter += 1
        
    plt.show()


def crowd_tracking(df_data, min_samples, generic=False):

    fig, axes = plt.subplots(nrows=2, ncols=1)
    counter = 0

    if not generic:
        common_macs = get_common_macs_for_tracking(df_data,min_samples)

    for df in df_data:
        grouped_df = df.groupby('mac')
        count = 0
        for name,group in grouped_df:
            group = group.resample('1T').mean().interpolate()
            group = group.strength.astype(int)
            if not generic:
                condition = name in common_macs
            else: 
                condition = len(group) > min_samples 

            if condition:
                #count += 1
                
                axes[counter].set_title("Devices tracked by Onion"+str(counter+1))
                axes[counter].set_ylabel("dBm")
                axes[counter].set_xlabel("Time",labelpad=30)
                axes[counter].grid('on', which='minor', axis='x')
                if name == "f4:1b:a1:26:cd:0c" or name == "64:a3:cb:69:58:9a" or name == "ec:35:86:e7:55:e0" or name == "58:48:22:d2:aa:9e":
                    group.plot(ax=axes[counter],kind='line',linestyle='-',legend=True,label=name,grid=True)
                else:
                    group.plot(ax=axes[counter],kind='line',linestyle=':',legend=True,label=name,grid=True)
                axes[counter].legend(loc='center left', bbox_to_anchor=(1,0.5))
                
        #print("count: %s" % str(count))
        counter += 1
    plt.show()

def device_types(unique_macs,min_count=0):
   
    fig1, ax1 = plt.subplots()

    company_list = {}
    """
    common_macs = get_common_macs_for_tracking(df_data)
    for mac in common_macs:
        company_list['mac'].append(mac)
        company_list['company'].append(parse_mac(mac))
    """
    for mac in unique_macs:
        company_list[mac] = parse_mac(mac)
    
    company_df = pd.DataFrame.from_dict(company_list, orient='index')
    company_df.columns = ['company']
    company_df = company_df.groupby(['company']).size() 
    company_df = company_df[company_df>min_count]    
    print(company_df)
    ax1.set_title("Device Type Statistics for Entire Monitoring Period")
    #ax1.pie(company_df, labels=company_df.index, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.pie(company_df, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    plt.legend(company_df.index,loc='lower left')
    #plt.legend(company_df.index,loc='upper center', bbox_to_anchor=(0.5, -0.05),  shadow=True, ncol=len(company_df.index))
    #plt.tight_layout()
    plt.show()

def main():

    df = []
    for i in range(1,len(sys.argv)):
        f_name = sys.argv[i]
        data = read_file(f_name)
        #data = filter_common_macs(data,"common_macs/common_macs.txt")
        df.append(data)

    """
    #df_compare(df)
    # Works well
    df_data = []  
    for i in df:
        df_data.append(filter_common_macs(i,"common_macs/common_macs.txt"))
   
    trimmed_df = trim_df(df_data)
    #crowd_tracking(trimmed_df,70,True)
    #crowd_tracking(trimmed_df,45,False)
    """

    #print(df[0]['mac'].tolist())
    
    #df = trim_df(df)

    macs = []
    for i in df:
        macs = macs + i['mac'].tolist()

    print(len(macs))
    unique_macs = list(set(macs))
    print(len(unique_macs))
    device_types(unique_macs,20) 
    

if __name__=="__main__":
    main()
