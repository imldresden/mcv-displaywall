#!/usr/bin/python

import sqlite3
import time

filename = 'balitmore_crime_db.sdb'

# create connection
conn = sqlite3.connect(filename)
print "Created and opened database successfully"

start_time = time.time()
cur = conn.cursor()
query = 'SELECT COUNT(crime_id) FROM crimes'
cur.execute(query)
print "Crimes in database: \t\t\t\t\t{}".format(cur.fetchone()[0])
print "Time needed for query: {:.10f} seconds\n".format(time.time()-start_time)

start_time = time.time()
query = 'SELECT COUNT(crime_id) FROM crimes INNER JOIN locations ON crimes.location_id=locations.location_id WHERE district_id=5'
cur.execute(query)
print "Crimes in the district SOUTHWESTERN: \t{}".format(cur.fetchone()[0])
print "Time needed for query: {:.10f} seconds\n".format(time.time()-start_time)

start_time = time.time()
query = 'SELECT COUNT(crime_id) FROM crimes WHERE weapon_id=2'
cur.execute(query)
print "Crimes with KNIFES: \t\t\t\t\t{}".format(cur.fetchone()[0])
print "Time needed for query: {:.10f} seconds\n".format(time.time()-start_time)

start_time = time.time()
query = "SELECT crime_id, (strftime('%w', datetime)) as dt FROM crimes WHERE dt>='1' AND dt<='2'"
cur.execute(query)
print "Crimes on Monday or Tuesday: \t\t\t{}".format(len(cur.fetchall()))
print "Time needed for query: {:.10f} seconds\n".format(time.time()-start_time)

start_time = time.time()
query = "SELECT crime_id, district_id FROM crimes INNER JOIN locations ON crimes.location_id=locations.location_id WHERE district_id=12 OR district_id=17"
cur.execute(query)
res = cur.fetchall()
print "Crimes on in the districts WESTERN or NORTHERN: \t{}\n --> {}".format(len(res), res)
print "Time needed for query: {:.10f} seconds\n".format(time.time()-start_time)


cur.close()
conn.close()