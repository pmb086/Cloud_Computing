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

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set('csv')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'cloud_secret'
# 
@app.route("/")
def home():
	return render_template('index.html')

# For render_template pass in name of template and any variables needed
@app.route("/upload", methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		csvfile = request.files['csvfile']
		file_name = secure_filename(request.files['csvfile'].filename).strip()
		request.files['csvfile'].save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
		conn = sql.connect('earth.db')
		df = pd.read_csv(app.config['UPLOAD_FOLDER'] + file_name)
		df.to_sql('EQ', conn, if_exists='replace', index=True)
		conn.close()
		flash('file uploaded successfully')
	return render_template('upload.html') 
	
@app.route("/view_data")
def view_data():
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ")
	rows = curs.fetchall()
	conn.close()
	return render_template('view_data.html', data=rows)	
	
@app.route('/search')
def search():
	return render_template('search.html')
	
@app.route('/search_success', methods=['GET', 'POST'])
def search_success():	
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ where mag > ?",(request.form['mag'],))
	rows = curs.fetchall()
	count = len(rows)
	conn.close()
	return render_template('search_success.html', data = rows, count = count)
	
@app.route('/magnitude')
def magnitude():
	return render_template('magnitude.html')
	
@app.route('/mag_success', methods=['GET', 'POST'])
def mag_success():	
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("Select * from EQ where mag >= ? and mag <= ?",(request.form['from'],request.form['to']))
	rows = curs.fetchall()
	conn.close()
	return render_template('mag_success.html', data = rows)
    
	
@app.route('/find_location')
def find_location():
    return render_template('find_location.html')
	
@app.route('/find_loc_success', methods=['GET', 'POST'])
def find_loc_success():
	lat1 = float(request.form['lat'])
	lon1 = float(request.form['long'])
	conn = sql.connect('earth.db')
	curs = conn.cursor()
	curs.execute("SELECT * FROM EQ")
	rows = curs.fetchall()
	result = []
	for r in rows:
		lat2 = float(r[2])
		lon2 = float(r[3])
		diff_lat = radians(lat2-lat1)
		diff_long = radians(lon2-lon1)
		a = sin(diff_lat/2) * sin(diff_lat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(diff_long/2) * sin(diff_long/2)
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		res = 6371 * c
		if res>=20 and res<=50:
			result.append(r)
	conn.close()
	count = len(result)
	return render_template('find_loc_success.html', data = result, count = count)

@app.route('/quest')
def quest():
    return render_template('quest.html')
	
@app.route('/quest_success', methods=['GET', 'POST'])
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

@app.route('/cluster')
def cluster():
    return render_template('cluster.html')

@app.route('/cluster_success', methods=['GET', 'POST'])
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
	plotter.savefig('static\clusterplot.jpg')
	
	return render_template('cluster_success.html',data = kmeans.cluster_centers_)
	
if __name__ == "__main__":
    app.run()


