import os
import json
import sys
from util import *
import requests

def consume():
    headers = {'Content-Type': 'application/vnd.kafka.v1+json', 'Accept': 'application/vnd.kafka.v1+json'}
    # Create a consumer
    r = requests.post("http://10.2.1.13:8082/consumers/wifi_streamers", json={'name': 'wifi_streamer_instance', 'format': 'json', 'auto.offset.reset': 'smallest'}, headers=headers)
    print(r.status_code, r.reason)


    headers = {'Content-Type': 'application/vnd.kafka.v1+json', 'Accept': 'application/vnd.kafka.v1+json'}
    # Subscribe the consumer
    r = requests.post("http://10.2.1.13:8082/consumers/wifi_streamers/instances/wifi_streamer_instance/subscription", json={'topics': 'wifi'}, headers=headers)
    print(r.status_code, r.reason)
    #consumers/my_json_consumer/instances/my_consumer_instance/subscription

    headers = {'Content-Type': 'application/vnd.kafka.v1+json'}
    # Get some records
    r = requests.get("http://10.2.1.13:8082/consumers/wifi_streamers/instances/wifi_streamer_instance/records", headers=headers)
    print(r.status_code, r.reason)


    headers = {'Content-Type': 'application/vnd.kafka.v1+json'}
    # Close consumer and delete stuff
    r = requests.delete("http://10.2.1.13:8082/consumers/wifi_streamers/instances/wifi_streamer_instance", headers=headers)
    print(r.status_code, r.reason)



def stream_process(KAFKA_IP, MYSQL_IP):

    consumer = connect_server("Kafka", KAFKA_IP)
    print("Connected to Kafka Broker!")
    conn = mysql_connect(MYSQL_IP,"root","elascale","wifi")
    print("Connected to MySQL Database!")

    # Initialize database tables
    execute_mysql_query(conn, "CREATE TABLE IF NOT EXISTS data (id INT AUTO_INCREMENT PRIMARY KEY, time_stamp DATETIME, onion VARCHAR(255), mac VARCHAR(255), strength SMALLINT, company VARCHAR(255));")
    execute_mysql_query(conn, "ALTER TABLE data ADD UNIQUE (time_stamp, onion, mac, strength);")
    print("created Database 'wifi' and table 'data'. Ready to ingest data...")

    proc_list = []

    for msg in consumer:
        store_data = {}
        data = json.loads(msg.value.decode('utf-8'))

        store_data['time_stamp'] = data['time_stamp'].rstrip()
        store_data['onion'] = stringify(data['onion'].rstrip())
        store_data['mac'] = stringify(data['mac'].rstrip())
        store_data['strength'] = int(data['strength'].rstrip())
        store_data['company'] = stringify(parse_mac(data['mac'].rstrip()))

        print(store_data)

        insert_mysql_query(conn,store_data)

        get_top_manufacturers = "select company, COUNT(*) from wifi.data where company not like '%None%' GROUP BY company ORDER BY count(*) DESC LIMIT 10;"
        fetch_mysql_query(conn,get_top_manufacturers)

        sys.stdout.flush()

    print("Shutting down Kafka and MySQL sessions...")

    consumer.close()
    conn['db'].close()
    sys.exit()

def main():
  # If testing at host, run this command before installing pip packages on host environment: sudo apt-get install libmysqlclient-dev
  #os.environ["KAFKA_IP"] = "10.2.1.13"
  #os.environ["MYSQL_IP"] = "10.2.1.12"
  #stream_process(os.environ["KAFKA_IP"], os.environ["MYSQL_IP"])
  consume()

  sys.exit()

if __name__=="__main__":
  main()
