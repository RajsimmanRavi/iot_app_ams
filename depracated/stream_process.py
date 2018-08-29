import json
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import sys
import time, threading
from datetime import datetime
from collections import Counter
import random
from multiprocessing import Process
from subprocess import Popen

# Connects to Kafka broker or Cassandra server and returns the connection result
def connect_server(server, IP):
  result = None
  while result is None:
    try:
      if server == "Kafka":
        result = KafkaConsumer('stats', bootstrap_servers=IP,request_timeout_ms=31000)
      else:
        cluster = Cluster([IP])
        result = cluster.connect()
    except KeyboardInterrupt:
      print("\nCaught Ctrl+C! Exiting Gracefully...")
      sys.exit()
    except Exception,e:
      print(str(e))
      print("Not connected yet. Reconnecting...")
      pass
  return result

def stream_process(KAFKA_IP, CASS_IP):

  consumer = connect_server("Kafka", KAFKA_IP)
  print("Connected to Kafka Broker!")
  session = connect_server("Cassandra", CASS_IP)
  print("Connected to Cassandra Database!")

  # Initialize database tables
  try:
    # Create keyspace 'stats'
    session.execute("CREATE KEYSPACE IF NOT EXISTS stats WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor':1};")
    # Create table 'data'
    session.execute("CREATE TABLE IF NOT EXISTS stats.data( data_id int PRIMARY KEY, mem_used text, mem_available text, tx_bytes bigint, rx_bytes bigint, cpu text, ps_cmd_output text, date text);")
  except Exception,e:
    print(str(e))
    consumer.close()
    session.shutdown()
    sys.exit()
  else: 
    print("created Keyspace 'stats' and table 'data'. Ready to ingest data...")

  proc_list = []

  for msg in consumer:
    data = json.loads(msg.value)

    rx_bytes = int(data['Network_received_bytes'])
    tx_bytes = int(data['Network_transmitted_bytes'])
    CPU = str(data['CPU'])
    mem_used = str(data['Memory_used'])
    mem_available = str(data['Memory_available'])
    ps_cmd_output = str(data['ps_command_output'])
    timestamp = str(data['Date'])

    parse_ps = ps_cmd_output.split("\n")[1:]
   
    for ps in parse_ps:
      proc = ps.split(" ")[-1]
      proc_list.append(proc)
    
    c = Counter(proc_list)

    file_name = "/tmp/counter"+str(random.randrange(0,100000000))    
    target = open(file_name, 'a')
    target.write(str(str(c)+"\n"))
    target.close()
     

    p = Popen("stress-ng --cpu 2 --cpu-load 5 -t 5 &", shell=True)         

    
    get_max_id = session.execute("SELECT MAX(data_id) from stats.data;")[0]
    
    for max_id in get_max_id:
      if max_id is not None:
        data_id = max_id + 1
      else:
        data_id = 1
     
    try: 
      session.execute_async("""INSERT INTO stats.data ( data_id, cpu, date, mem_available, mem_used, rx_bytes, tx_bytes, ps_cmd_output) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """, (data_id, CPU, timestamp, mem_available, mem_used, rx_bytes, tx_bytes, ps_cmd_output))
    except Exception,e:
      print("Could not insert data to table...")
      print(str(e))
    else:
      print("Successfully stored data in Cassandra database!")

    sys.stdout.flush()
    
  print("Shutting down Kafka and Cassandra sessions...")

  consumer.close()
  session.shutdown()
  sys.exit()

def main():
  KAFKA_IP = sys.argv[1]
  CASS_IP = sys.argv[2]

  stream_process(KAFKA_IP, CASS_IP)

  sys.exit()
  """
  processes = []

  for m in range(1, 20):
    p = Process(target=stream_process, args=(KAFKA_IP,CASS_IP))
    p.start()
    processes.append(p)

  for p in processes:
    p.join()
  """

if __name__=="__main__":
  main()

