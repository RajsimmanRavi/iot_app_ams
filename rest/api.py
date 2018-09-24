from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
import json
from util import *
import os

#os.environ["MYSQL_IP"] = "10.2.1.12"
#os.environ["HOST_PORT"] = "6969"

MYSQL_IP = os.environ["MYSQL_IP"]
REST_API_PORT = os.environ["REST_API_PORT"]

conn = mysql_connect(MYSQL_IP,"root","elascale","wifi")
print("Connected to MySQL Database!")

# Initialize database tables
execute_mysql_query(conn, "CREATE TABLE IF NOT EXISTS data (id INT AUTO_INCREMENT PRIMARY KEY, time_stamp DATETIME, onion VARCHAR(255), mac VARCHAR(255), strength SMALLINT, company VARCHAR(255));")
execute_mysql_query(conn, "ALTER TABLE data ADD UNIQUE (time_stamp, onion, mac, strength);")
print("created Database 'wifi' and table 'data'. Ready to ingest data...")

class FetchDataHandler(tornado.web.RequestHandler):

    def post(self):

        store_data = {}

        data = tornado.escape.json_decode(self.request.body)

        store_data['time_stamp'] = stringify(data['time_stamp'].rstrip())
        store_data['onion'] = stringify(data['onion'].rstrip())
        store_data['mac'] = stringify(data['mac'].rstrip())
        store_data['strength'] = int(data['strength'].rstrip())
        store_data['company'] = stringify(parse_mac(data['mac'].rstrip()))

        print(store_data)

        insert_mysql_query(conn,store_data)

        sys.stdout.flush()

    def get(self):

        get_top_manufacturers = "select company, COUNT(*) from wifi.data where company not like '%None%' GROUP BY company ORDER BY count(*) DESC LIMIT 10;"
        top_manufacturers = fetch_mysql_query(conn,get_top_manufacturers)

        self.write(top_manufacturers)

class InfoHandler(tornado.web.RequestHandler):

     def get(self):
        response = { 'info': 'This API is basically used to send Wifi Data to MySQL DB and can fetch top device manufacturers (based on MAC) of the collected data',
                     'handlers': '/ (GET) and /data (GET AND POST)'}
        self.write(response)

application = tornado.web.Application([
    (r"/data", FetchDataHandler),
    (r"/", InfoHandler)
])

if __name__ == "__main__":
    application.listen(REST_API_PORT)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("closing----")
        conn["db"].close()
        tornado.ioloop.IOLoop.instance().stop()
