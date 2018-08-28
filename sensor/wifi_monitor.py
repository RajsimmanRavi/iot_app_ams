from scapy.all import *
import subprocess as sp
import re
import os
import json
import datetime
import csv

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

def read_files(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith(".pcap"):
            print("FILE_NAME: %s" %file_name)
            sniff(offline=os.path.join(directory,file_name),prn=parse_pkt, store=0)


def parse_pkt(pkt):

    fmt = "%Y/%m/%d %H:%M:%S"

    if pkt.haslayer(Dot11) and pkt.type==0 and pkt.subtype==4:

        epoch = pkt.time
        time = datetime.datetime.fromtimestamp(float(epoch))
        #orig_time = time.strftime(fmt)

        if time.date() == datetime.date(2016, 8, 19):
            new_epoch = epoch+(51630+180+(3600*4))
        else:
            new_epoch = epoch+(3600*4)

        time = datetime.datetime.fromtimestamp(float(new_epoch))
        correct_time = time.strftime(fmt)

        mac = pkt[Dot11].addr2
        signal_strength = -(256-ord(pkt.notdecoded[-2:-1]))

        string = "%s,%s,%s\n" %(correct_time, mac, signal_strength)

        with open("/home/xxxx/wifi_manilla/onion1297.csv",'a') as fd:
            fd.write(string)

        return string

        """
        if mac:
            prefix = mac.replace(":","")[0:6]
            cmd = "grep -i "+prefix+" oui.txt"
            lookup = mac_lookup(cmd)
            outp = "MAC: %s Company: %s" %(mac,lookup)
            print(outp)
            return outp
        """

def main():
    #read_files("/home/xxxx/wifi_manilla/data/raw_data/onion233E/")
    read_files("/home/xxxx/wifi_manilla/data/raw_data/onion1297/")

if __name__=="__main__":
    main()

