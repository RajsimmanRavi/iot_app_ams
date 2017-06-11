import json
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import sys

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

def main():
  KAFKA_IP = sys.argv[1]
  CASS_IP = sys.argv[2]

  consumer = connect_server("Kafka", KAFKA_IP)
  print("Connected to Kafka Broker!")
  session = connect_server("Cassandra", CASS_IP)
  print("Connected to Cassandra Database!")

  # Initialize database tables
  try:
    # Create keyspace 'stats'
    session.execute("CREATE KEYSPACE IF NOT EXISTS stats WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor':1};")
    # Create table 'data'
    session.execute("CREATE TABLE IF NOT EXISTS stats.data( data_id int PRIMARY KEY, mem_used text, mem_available text, tx_bytes bigint, rx_bytes bigint, cpu text, date text);")
  except Exception,e:
    print(str(e))
    consumer.close()
    session.shutdown()
    sys.exit()
  else: 
    print("created Keyspace 'stats' and table 'data'. Ready to ingest data...")

  for msg in consumer:
    data = json.loads(msg.value)

    rx_bytes = int(data['Network_received_bytes'])
    tx_bytes = int(data['Network_transmitted_bytes'])
    CPU = str(data['CPU'])
    mem_used = str(data['Memory_used'])
    mem_available = str(data['Memory_available'])
    timestamp = str(data['Date'])

    get_max_id = session.execute("SELECT MAX(data_id) from stats.data;")[0]
    
    for max_id in get_max_id:
      if max_id is not None:
        data_id = max_id + 1
      else:
        data_id = 1
 
    try: 
      session.execute_async("""INSERT INTO stats.data ( data_id, cpu, date, mem_available, mem_used, rx_bytes, tx_bytes) VALUES (%s, %s, %s, %s, %s, %s, %s) """, (data_id, CPU, timestamp, mem_available, mem_used, rx_bytes, tx_bytes))
    except:
      print("Could not insert data to table...")
    else:
      print("Successfully stored data in Cassandra database!")
    
  print("Shutting down Kafka and Cassandra sessions...")

  consumer.close()
  session.shutdown()
  sys.exit()

if __name__=="__main__":
  main()

