import os
import json
import sys
from util import *

def stream_process(KAFKA_IP, MYSQL_IP):

    consumer = connect_server("Kafka", KAFKA_IP)
    print("Connected to Kafka Broker!")
    conn = mysql_connect("10.2.1.11","root","elascale","wifi")
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
  os.environ["KAFKA_IP"] = "10.2.1.11"
  os.environ["MYSQL_IP"] = "10.2.1.11"

  stream_process(os.environ["KAFKA_IP"], os.environ["MYSQL_IP"])

  sys.exit()

if __name__=="__main__":
  main()
