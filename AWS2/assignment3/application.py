import os
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import sqlite3 as sql
import random
import redis
from time import time
"""
	Name : Balaji Paiyur Mohan
	UTA ID: 1001576836

"""
application = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set('csv')

TTL = 25
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = 'cloudydreams'
 
@application.route("/")
def home():
	return render_template('index.html')

# For render_template pass in name of template and any variables needed
@application.route("/upload", methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		csvfile = request.files['csvfile']
		file_name = secure_filename(request.files['csvfile'].filename).strip()
		request.files['csvfile'].save(os.path.join(application.config['UPLOAD_FOLDER'], file_name))
		#conn = ibm_db.connect("DATABASE=BLUDB ;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;UID=nqf07957;PWD=wcg9ptq@c9kst5m0;","","")
		conn = sql.connect('earth.db')
		df = pd.read_csv(application.config['UPLOAD_FOLDER'] + file_name)
		df.to_sql('Data', conn, if_exists='replace', index=True)
		#ibm_db.close(conn)
		conn.close()
		#flash('file uploaded successfully')
	return render_template('upload.html') 
	
@application.route("/view_data", methods=['GET', 'POST'])
def view_data():
	"""conn = ibm_db.connect("DATABASE=BLUDB ;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;UID=nqf07957;PWD=wcg9ptq@c9kst5m0;","","")
	query = "Select * from EQ"
	rows = []
	ibm_db.execute(query)
	res = ibm_db.fetch_assoc(query)
	while res is True:
		rows.append(result.copy())
		res = ibm_db.fetch_assoc(query)
	ibm_db.close(conn)"""
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("DELETE FROM Data WHERE rms <= 0.25")
	curs.execute("Select * from Data")
	rows = curs.fetchall()
	count = len(rows)
	conn.close()
	return render_template('view_data.html', data=rows, count= count)	
	
@application.route('/query_gen')
def query_gen():
	return render_template('query_gen.html')
	
@application.route('/query_gen_success', methods=['GET', 'POST'])
def query_gen_success():
	#conn = ibm_db.connect("DATABASE=BLUDB ;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;UID=nqf07957;PWD=wcg9ptq@c9kst5m0;","","")
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	num = int(request.form['query'])
	start = time()
	par = 0
	rows = []
	for i in range(1,num):
		par = random.uniform(0.5,7.5)
		query = "Select * from Data where mag >= " + str(par)	
		curs.execute(query)
		rows = curs.fetchall()
		"""ibm_db.execute(query)
		res = ibm_db.fetch_assoc(query)
		while res is True:
			rows.append(result.copy())
			res = ibm_db.fetch_assoc(query)"""
	stop = time()
	exec_time = stop - start
	#ibm_db.close(conn)
	conn.close()
	return render_template('query_gen_success.html', data = rows, exe = exec_time)

@application.route('/cached_query')
def cached_query():
    return render_template('cached_query.html')
	
@application.route('/cached_query_success', methods=['GET', 'POST'])
def cached_query_success():
	#conn = ibm_db.connect("DATABASE=BLUDB ;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;UID=nqf07957;PWD=wcg9ptq@c9kst5m0;","","")
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	num = int(request.form['query'])	
	par = 0
	#con = memcache.Client(['127.0.0.1:11211'],debug=0)
	con = redis.StrictRedis(host='cloud6.iuvuml.ng.0001.use2.cache.amazonaws.com', port=6379, db=0)
	#print(num)
	data = []
	lists = []
	start1 = time()
	for i in range(1,num):
		par = round(random.uniform(0.5,7.5),1)
		query = "Select * from Data where mag >= " + str(par)
		key = str(par)
		r = con.get(key)
		if r:
			data.append('cached')
			lists.append(r)
		else:
			data.append('not cached')
			#start1 = time()
			#stop1 = time()
			#s = time()
			#ibm_db.execute(query)
			curs.execute(query)
			#print(time()-s,i)
			#s = time()
			rows = curs.fetchall()
			lists.append(rows)
			# res = ibm_db.fetch_assoc(query)
			# while res is True:
				# rows.append(result.copy())
				# res = ibm_db.fetch_assoc(query)
			#print(time()-s,i)
			#s = time()
			con.set(key,rows,TTL)
			#print(time()-s,i)
	#ibm_db.close(conn)
	stop1 = time()
	exec_time = stop1 - start1
	conn.close()
	return render_template('cached_query_success.html', zip= zip(data, lists), exe = exec_time)

@application.route('/loc_query')
def loc_query():
    return render_template('loc_query.html')
	
@application.route('/loc_query_success', methods=['GET', 'POST'])
def loc_query_success():
	#conn = ibm_db.connect("DATABASE=BLUDB ;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;PORT=50000;UID=nqf07957;PWD=wcg9ptq@c9kst5m0;","","")
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	num = int(request.form['query1'])
	loc = str(request.form['query'])
	q = "Select net from Data where net LIKE '"+loc+"%'"
	curs.execute(q)
	rows = curs.fetchall()
	print(rows)
	loclist =set(rows)
	
	#con = memcache.Client(['127.0.0.1:11211'],debug=0)
	con = redis.StrictRedis(host='cloud6.iuvuml.ng.0001.use2.cache.amazonaws.com', port=6379, db=0)
	#print(num)
	data = []
	lists = []
	start1 = time()
	for i in range(1,num):
		par = random.choice(loclist)
		query = "Select id from Data where id like " + str(par)
		key = str(par)
		r = con.get(key)
		if r:
			data.append('cached')
			lists.append(r)
		else:
			data.append('not cached')
			#start1 = time()
			#stop1 = time()
			#s = time()
			#ibm_db.execute(query)
			curs.execute(query)
			#print(time()-s,i)
			#s = time()
			rows = curs.fetchall()
			lists.append(rows)
			# res = ibm_db.fetch_assoc(query)
			# while res is True:
				# rows.append(result.copy())
				# res = ibm_db.fetch_assoc(query)
			#print(time()-s,i)
			#s = time()
			con.set(key,rows,TTL)
			#print(time()-s,i)
	#ibm_db.close(conn)
	stop1 = time()
	exec_time = stop1 - start1
	conn.close()
	return render_template('loc_query_success.html', zip= zip(data, lists), exe = exec_time)

@application.route('/restrict')
def restrict():
	return render_template('restrict.html')
	
@application.route('/restrict_success', methods=['GET', 'POST'])
def restrict_success():
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	start2 = time()
	curs.execute("Select * from Data where ? = ?",(request.form['par'],request.form['value']))
	rows = curs.fetchall()
	stop2 = time()
	exec_time2 = stop2 - start2
	conn.close()
	count = len(rows)
	return render_template('restrict_success.html', data = rows, exe = exec_time2)

if __name__ == "__main__":
	application.run()
