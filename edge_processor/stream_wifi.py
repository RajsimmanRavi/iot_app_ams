import os
import re
import json
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import sys
import subprocess as sp

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

def parse_data(mac):
  mac = mac['mac']
  prefix = mac.replace(":","")[0:6]
  cmd = "grep -i "+prefix+" /usr/src/edge_processor/oui.txt"
  #cmd = "grep -i "+prefix+" oui.txt"
  lookup = mac_lookup(cmd)
  send_data = "%s Company: %s" %(mac,lookup)
  return send_data

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
    except Exception as e:
      print(str(e))
      print("Not connected yet. Reconnecting...")
      pass
  return result

def execute_query(session, command):
    try:
      output = session.execute(command)[0]
    except Exception as e:
      print("Could not execute query: %s..." % command)
      print(str(e))
    else:
      print("Successfully executed query: %s on Cassandra database!" % command)
      return output

def stringify(data):
    return "'%s'" % data

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
    session.execute("CREATE TABLE IF NOT EXISTS stats.data( data_id int PRIMARY KEY, time text, mac text, signal text );")
  except Exception as e:
    print(str(e))
    consumer.close()
    session.shutdown()
    sys.exit()
  else:
    print("created Keyspace 'stats' and table 'data'. Ready to ingest data...")

  proc_list = []

  for msg in consumer:
    #data = json.loads(msg.value.decode('utf-8'))
    data = json.loads(msg.value.decode('utf-8'))
    pkt_data = parse_data(data)

    split_data = pkt_data.split(",")

    time = stringify(split_data[0].rstrip())
    mac = stringify(split_data[1.rstrip())
    strength = stringify(split_data[2].rstrip())

    print("time: %s mac: %s strength: %s" %(time,mac,strength))

    query_max_id = "SELECT MAX(data_id) from stats.data;"
    get_max_id = execute_query(session, query_max_id)

    for max_id in get_max_id:
      if max_id is not None:
        data_id = max_id + 1
      else:
        data_id = 1

    query_mac = "SELECT * from stats.data WHERE mac=%s ALLOW FILTERING;" % mac
    get_mac = execute_query(session, query_mac)

    if not get_mac:
        insert_query = "INSERT INTO stats.data ( data_id, mac, company) VALUES (%s, %s, %s);" % (data_id, mac, company)
        insert_output = execute_query(session, insert_query)

    sys.stdout.flush()

  print("Shutting down Kafka and Cassandra sessions...")

  consumer.close()
  session.shutdown()
  sys.exit()

def main():
  #os.environ["KAFKA_IP"] = "10.2.1.11"
  #os.environ["CASS_IP"] = "10.2.1.11"

  stream_process(os.environ["KAFKA_IP"], os.environ["CASS_IP"])

  sys.exit()

if __name__=="__main__":
  main()
