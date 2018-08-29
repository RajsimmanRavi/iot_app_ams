from subprocess import Popen, call, PIPE, STDOUT
import socket
import sys
import time
import base64
import datetime
from kafka import KafkaProducer
import json

# This function is used to perform the linux commmands 
def cmd_output(cmd):
  ps = Popen(cmd,shell=True,stdout=PIPE,stderr=STDOUT)
  output = ps.communicate()[0]
  output = str(output.rstrip()).strip("\\").strip('b').strip("/").strip("'")
  return output

# Fetches stats and sends it to appropriate endpoint in JSON format (kinda)
def get_stats(UDP_IP, UDP_PORT):

  # The following strings are the linux commands
  cpu_cmd='grep cpu /proc/stat | awk \'{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}\''
  mem_cmd = 'free -tmh | grep Mem | tr -s \' \' | awk \'{print $3","$7","$2}\''
  network_cmd='cat /proc/net/dev | tr -s \' \' | grep eth0 | awk \'{print $2","$10}\''
  ps_cmd = 'ps'

  # Call cmd_output function to get the output of the executed commands
  cpu = cmd_output(cpu_cmd)
  mem = cmd_output(mem_cmd)
  network = cmd_output(network_cmd)
  ps = cmd_output(ps_cmd)  

  parse_mem = mem.split(",")
  used_mem = parse_mem[0]
  available_mem = parse_mem[1]
  total_mem = parse_mem[2]

  parse_network = network.split(",")
  rcv_bytes = parse_network[0]
  trans_bytes = parse_network[1]
  # build json object
  data = {}
  data['Date'] = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
  data['CPU'] = cpu
  data['Memory_used'] = used_mem
  data['Memory_available'] = available_mem
  data['Network_received_bytes'] = rcv_bytes
  data['Network_transmitted_bytes'] = trans_bytes
  data['ps_command_output'] = str(ps)

  print(str(data))

  json_data = json.dumps(data)
  
  # send data to Kafka consumer 
  try:
    kafka_server = UDP_IP+":"+str(UDP_PORT)
    producer = KafkaProducer(bootstrap_servers=kafka_server)
    producer.send('stats', json_data.encode('utf8'))
    producer.flush()
    producer.close()
  except Exception, e:
    print("Error occurred during data transmission process!")
    print(str(e))
    pass
  else:
    print("Successfully transmitted data!")
   
def main():

  UDP_IP = sys.argv[1]
  UDP_PORT = int(sys.argv[2])
  
  while 1:
    timestamp = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    print("Starting data collection and transmission for: "+str(timestamp))
    sys.stdout.flush()
    get_stats(UDP_IP, UDP_PORT)
    sys.stdout.flush()
    time.sleep(5)
  
  sys.exit()

if __name__=="__main__":
  main()

