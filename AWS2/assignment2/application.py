import os
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
from math import atan2,cos, sin, sqrt, radians
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib as mp
mp.use('Agg')
import matplotlib.pyplot as plotter
import sqlite3 as sql
"""
	Name : Balaji Paiyur Mohan
	UTA ID: 1001576836

"""
application = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set('csv')

application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = 'cloud_secret'
# 
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
		conn = sql.connect('earth.db')
		df = pd.read_csv(application.config['UPLOAD_FOLDER'] + file_name)
		df.to_sql('EQ', conn, if_exists='replace', index=True)
		conn.close()
		flash('file uploaded successfully')
	return render_template('upload.html') 
	
@application.route("/view_data")
def view_data():
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ")
	rows = curs.fetchall()
	conn.close()
	return render_template('view_data.html', data=rows)	
	
@application.route('/search')
def search():
	return render_template('search.html')
	
@application.route('/search_success', methods=['GET', 'POST'])
def search_success():	
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ where mag > ?",(request.form['mag'],))
	rows = curs.fetchall()
	count = len(rows)
	conn.close()
	return render_template('search_success.html', data = rows, count = count)
	
@application.route('/magnitude')
def magnitude():
	return render_template('magnitude.html')
	
@application.route('/mag_success', methods=['GET', 'POST'])
def mag_success():	
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ where mag >= ? and mag <= ?",(request.form['from'],request.form['to']))
	rows = curs.fetchall()
	conn.close()
	return render_template('mag_success.html', data = rows)
    
	
@application.route('/find_location')
def find_location():
    return render_template('find_location.html')
	
@application.route('/find_loc_success', methods=['GET', 'POST'])
def find_loc_success():
	lat1 = float(request.form['lat'])
	lon1 = float(request.form['long'])
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("SELECT * FROM EQ")
	rows = curs.fetchall()
	result1 = []
	result2 = []
	result3 = []
	for r in rows:
		lat2 = float(r[2])
		lon2 = float(r[3])
		diff_lat = radians(lat2-lat1)
		diff_long = radians(lon2-lon1)
		a = sin(diff_lat/2) * sin(diff_lat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(diff_long/2) * sin(diff_long/2)
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		res = 6371 * c
		if res<=20:
			result1.append(r)
		elif res>20 and res<50:
			result2.append(r)
		elif res>=50:
			result3.append(r)
	conn.close()
	count1 = len(result1)
	count2 = len(result2)
	count3 = len(result3)
	return render_template('find_loc_success.html', data1 = result1, count1 = count1, data2 = result2, count2 = count2, data3 = result3, count3 = count3)

@application.route('/quest')
def quest():
    return render_template('quest.html')
	
@application.route('/quest_success', methods=['GET', 'POST'])
def quest_success():
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ where (((time like '%T20%') or (time like '%T21%') or (time like '%T22%') or (time like '%T23%') or  (time like '%T00%') or  (time like '%T01%')  or  (time like '%T02%')  or  (time like '%T03%') or  (time like '%T04%') or  (time like '%T05%')) and (mag > ?))",(request.form['mag'],))
	rows = curs.fetchall()
	count = len(rows)
	curs.execute("Select * from EQ where (((time not like '%T20%') or (time not like '%T21%') or (time not like '%T22%') or (time not like '%T23%') or (time not like '%T00%') or (time not like '%T01%')  or  (time not like '%T02%')  or  (time not like '%T03%') or  (time not like '%T04%') or (time not like '%T05%')) and (mag > ?))",(request.form['mag'],))
	rows2 = curs.fetchall()
	count2 = len(rows2)
	conn.close()
	return render_template('quest_success.html', count = count,count2 = count2, data = rows, data2 = rows2)

@application.route('/cluster')
def cluster():
    return render_template('cluster.html')

@application.route('/cluster_success', methods=['GET', 'POST'])
def cluster_success():
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("SELECT latitude,longitude FROM EQ")
	rows = curs.fetchall()
	df = pd.DataFrame(rows)
	plotter.title('Clustering of Earthquakes\n', fontsize=15)
	k_clusters = request.form['cluster']
	#plotter.figure(figsize=(900/150, 900/150), dpi=150)
	plotter.xlabel('Latitude', fontsize=14)
	plotter.ylabel('Longitude', fontsize=14)
	plotter.scatter(df.iloc[:,0], df.iloc[:,1], c='b', label = 'Earthquake locations')
	kmeans= KMeans(n_clusters=int(k_clusters)).fit(pd.DataFrame(rows))
	centroids = kmeans.cluster_centers_
	df2= pd.DataFrame(centroids)
	plotter.scatter(df2.iloc[:,0], df2.iloc[:,1], c='r', label ='Centroids')
	plotter.legend(loc="upper right")
	plotter.savefig('static/clusterplot.png')
	
	return render_template('cluster_success.html',data = kmeans.cluster_centers_)
	
@application.route('/loc_source')
def loc_source():
	return render_template('loc_source.html')
	
@application.route('/loc_source_success', methods=['GET', 'POST'])
def loc_source_success():
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select time, latitude, longitude, place from EQ where locationSource = ? and mag > ? and magNst * 2 >= nst",(request.form['source'],request.form['mag']))
	rows = curs.fetchall()
	conn.close()
	count = len(rows)
	return render_template('loc_source_success.html', data = rows, count = count)

@application.route('/find_largest')
def find_largest():
	return render_template('find_largest.html')
	
@application.route('/find_largest_success', methods=['GET', 'POST'])	
def find_largest_success():
	lat1 = float(32.7357)
	lon1 = float(-97.1081)
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("SELECT time,latitude,longitude,place FROM EQ")
	rows = curs.fetchall()
	result1 = []
	result2 = []
	result3 = []
	for r in rows:
		lat2 = float(r[2])
		lon2 = float(r[3])
		diff_lat = radians(lat2-lat1)
		diff_long = radians(lon2-lon1)
		a = sin(diff_lat/2) * sin(diff_lat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(diff_long/2) * sin(diff_long/2)
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		res = 6371 * c
		if res<=100:
			result1.append(r)
	conn.close()
	count1 = len(result1)
	return render_template('find_loc_success.html', data1 = result1, count1 = count1)

if __name__ == "__main__":
    application.run()


