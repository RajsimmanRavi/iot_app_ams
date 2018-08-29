#!/usr/bin/python
import MySQLdb

def mysql_connect(host_ip,user_name,password,database):

    conn = {}
    db = MySQLdb.connect(host=host_ip,
                         user=user_name,
                         passwd=password,
                         db=database)

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    conn["cursor"] = cur
    conn["db"] = db

    return conn

def execute_mysql_query(conn,cmd):
    result = None
    while result is None:
        try:
             conn["cursor"].execute(cmd)
        except Exception as e:
             print("Error occurred while executing... %s" % e)
             pass
        else:
            print("Successfully executed query: %s on MySQL database!" % cmd)
            result = "Complete"

def insert_mysql_query(conn,data):

    try:
        conn["cursor"].execute("""INSERT INTO wifi.data (time_stamp,onion,mac,strength) VALUES (%s,%s,%s,%s)""", (data["time_stamp"],data["onion"],data["mac"],data["strength"]))
        conn["db"].commit()
    except Exception as e:
        print("Error occurred while executing... %s" % e)
        conn["db"].rollback
    else:
        print("Done")

def fetch_mysql_query(conn):

    try:
        conn["cursor"].execute("select * from wifi.data;")
    except Exception as e:
        print("Error occurred while executing... %s" % e)
    else:
        print("Done")
        #r = conn["cursor"].store_result()
        rows = conn["cursor"].fetchall()
        for row in rows:
            print(row)

def main():
    conn = mysql_connect("xx","xx","xx","xx")

    execute_mysql_query(conn, "CREATE TABLE IF NOT EXISTS data (id INT AUTO_INCREMENT PRIMARY KEY, time_stamp DATETIME, onion VARCHAR(255), mac VARCHAR(255), strength SMALLINT);")
    execute_mysql_query(conn, "ALTER TABLE data ADD UNIQUE (time_stamp, onion, mac, strength);")

    data = {}

    data["time_stamp"] = '2016-08-20 08:41:57'
    data["onion"] = 'onion233E'
    data["mac"] = '96:68:43:db:c3:b1'
    data["strength"] = -35

    #"""INSERT INTO stats.data (time_stamp,onion,mac,strength) VALUES (%s,%s,%s,%s)""", ('2016-08-20 08:41:57','onion233E','96:68:43:db:c3:b0',-35)
    insert_mysql_query(conn,data)
    fetch_mysql_query(conn)

    conn['db'].close()

if __name__=="__main__":
    main()
