from scapy.all import *
import subprocess as sp
import re
import os
import json

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
            check = sniff(offline=os.path.join(directory,file_name),prn=parse_pkt, store=0)
            print(check)


def parse_pkt(pkt):
    data = {}
    data['data'] = bytes(pkt)

    json_data = json.dumps(data)

    print(str(data))

    if data['data'].haslayer(Dot11):
        epoch = pkt.time
        mac = pkt[Dot11].addr2
        if mac:
            prefix = mac.replace(":","")[0:6]
            cmd = "grep -i "+prefix+" oui.txt"
            lookup = mac_lookup(cmd)
            outp = "MAC: %s Company: %s" %(mac,lookup)
            print(outp)
            return outp

def main():
    read_files("/home/ubuntu/onion233E/")

if __name__=="__main__":
    main()

