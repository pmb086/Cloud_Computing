import os
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib as mp
mp.use('Agg')
import matplotlib.pyplot as plotter
#from matplotlib import cm
import sqlite3 as sql
"""
	Name : Balaji Paiyur Mohan
	UTA ID: 1001576836

"""
application = Flask(__name__)
application.debug=True
#port = int(os.getenv('PORT', 8000))

scaler = StandardScaler()
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set('csv')

#colors = np.random.rand(50)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = 'cloud_secret'

@application.route("/")
def home():
	return render_template('index.html')

# For render_template pass in name of template and any variables needed
@application.route("/upload", methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		xlsfile = request.files['xlsfile']
		file_name = secure_filename(request.files['xlsfile'].filename)
		request.files['xlsfile'].save(os.path.join(application.config['UPLOAD_FOLDER'], file_name))
		conn = sql.connect('titanic.db')
		df = pd.read_csv(application.config['UPLOAD_FOLDER'] + file_name , na_values='NaN')
		df.to_sql('people', conn, if_exists='replace', index=True)
		conn.close()
		flash('file uploaded successfully')
	return render_template('upload.html') 
	
@application.route("/view_data")
def view_data():
	conn = sql.connect('titanic.db')
	curs = conn.cursor()
	curs.execute("Select * from people")
	rows = curs.fetchall()
	conn.close()
	return render_template('view_data.html', data=rows)	

@application.route('/cluster')
def cluster():
    return render_template('cluster.html')

@application.route('/cluster_success', methods=['GET', 'POST'])
def cluster_success():
	conn = sql.connect('titanic.db')
	curs = conn.cursor()
	curs.execute("SELECT age, fare price FROM people")
	rows = curs.fetchall()
	df_unscaled = pd.DataFrame(rows)
	df_unscaled = df_unscaled.dropna(axis=0, how='any')
	df = scaler.fit_transform(df_unscaled)
	df = pd.DataFrame(df)
	plotter.title('Clustering of people\n', fontsize=15)
	k_clusters = request.form['cluster']
	#count no of NaN isnull().sum()
	kmeans= KMeans(n_clusters=int(k_clusters)).fit(df)
	#plotter.figure(figsize=(900/150, 900/150), dpi=150)
	plotter.xlabel('Age', fontsize=14)
	plotter.ylabel('Fare price', fontsize=14)
	plotter.scatter(df.iloc[:,0], df.iloc[:,1], c=[i.astype(float) for i in kmeans.labels_])#, label = ["cluster"+str(i) for i in range(1,int(k_clusters))])
	centroids = kmeans.cluster_centers_
	centroid_pts = kmeans.labels_
	df2= pd.DataFrame(centroids)	
	count1 = df2.shape[0]
	count2 = df.dropna(axis=0, how='any').shape[0]
	plotter.scatter(df2.iloc[:,0], df2.iloc[:,1], c='r',marker = "^", label ='Centroids')
	#plotter.legend(loc="upper right")
	plotter.savefig('static/clusterplot')
	plotter.clf()
	count = 0
	#count clusters
	counter = {}
	for i in range(0,int(k_clusters)):
		for j in centroid_pts:
			if j == i:
				count=count+1
		counter[i] = count
		count=0
	#distance
	distance ={}
	for i in range(0,int(k_clusters)):
		for j in range(i,int(k_clusters)):
			if i != j:
				dist = np.linalg.norm(centroids[i]-centroids[j])
				key = '('+ str(i) +',' + str(j) +')'
				distance[str(key)] = dist
	#elbow
	distortions = {}
	c_range = range(2,10)
	#silhouette score
	score_stats = {}
	for i in c_range:
		clust = KMeans(i).fit(pd.DataFrame(rows).dropna(axis=0, how='any'))
		distortions[i] = clust.inertia_	
		k_means = KMeans(i).fit(pd.DataFrame(rows).dropna(axis=0, how='any'))
		silhouette_avg_score = silhouette_score(pd.DataFrame(rows).dropna(axis=0, how='any'), clust.labels_)
		score_stats[i] = "The average silhouette score value is : "+ str(silhouette_avg_score)
	plotter.plot(distortions.keys(),distortions.values())
	plotter.xlabel("Number of clusters")
	plotter.ylabel("Explained Variance")
	plotter.title("Elbow method results")
	plotter.savefig('static/elbow')
	plotter.clf()
	
	return render_template('cluster_success.html',zip = zip(centroids, centroid_pts), count1 = count1, count2 = count2,counter = counter,score_stats = score_stats, distance = distance)
	
@application.route('/earth')
def earth():
    return render_template('earth.html')

@application.route('/earth_success', methods=['GET', 'POST'])
def earth_success():
	conn = sql.connect('titanic.db')
	curs = conn.cursor()
	a1 = int(request.form['from'])
	a2 = int(request.form['to'])
	par = request.form['par']
	query = 'SELECT COUNT(*) FROM people where ' +str(par) + '>= ' +str(a1) + ' and ' +str(par) + '<=' +str(a2) 
	curs.execute(query)
	rows = curs.fetchall()
	listdata = []
	column = ['range', 'values']
	listdata.append(column)
	while a1 <= a2:
			q = 'SELECT COUNT(*) FROM people where ' +str(par) + ' >= ' +str(a1) + ' and ' +str(par) + ' <= ' + str(a1+0.5)
			curs.execute(q)
			rows = curs.fetchall()
			c = rows[0][0]
			st = str(a1) +' - '+ str(int(a1)+0.5)
			a1 = a1 + 0.5
			listdata.append([st,c])
	conn.close()
	return render_template('earth_success.html', data=listdata)	
"""	
@application.route('/titanic')
def titanic():
	return render_template('titanic.html')
"""
@application.route('/titanic_success', methods=['GET', 'POST'])
def titanic_success():	
	conn = sql.connect('titanic.db')
	curs = conn.cursor()
	#survived_male
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'male' and survived = 1 group by sex, survived, pclass")
	rows1 = curs.fetchall()
	mlistdata = []
	mlistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows1:
		pclass = 'Class' + str(i[0])
		count = i[1]
		mlistdata.append([pclass,count,"yellow"])
	print(mlistdata)
	#survived_female
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'female' and survived = 1 group by sex, survived, pclass")
	rows2 = curs.fetchall()
	flistdata = []
	flistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows2:
		pclass = 'Class' + str(i[0])
		count = i[1]
		flistdata.append([pclass,count,"blue"])
	#not_survived_male
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'male' and survived = 0 group by sex, survived, pclass")
	rows3 = curs.fetchall()
	nmlistdata = []
	nmlistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows3:
		pclass = 'Class' + str(i[0])
		count = i[1]
		nmlistdata.append([pclass,count,"green"])
	#not_survived_female
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'male' and survived = 0 group by sex, survived, pclass")
	rows4 = curs.fetchall()
	nflistdata = []
	nflistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows4:
		pclass = 'Class' + str(i[0])
		count = i[1]
		nflistdata.append([pclass,count,"red"])
	conn.close()
	return render_template('titanic_success.html', data1 = mlistdata, data2 = flistdata, data3 = nmlistdata, data4 = nflistdata)
	
@application.route('/Bearth')
def Bearth():
    return render_template('Bearth.html')

@application.route('/Bearth_success', methods=['GET', 'POST'])
def Bearth_success():
	conn = sql.connect('titanic.db')
	curs = conn.cursor()
	a1 = int(request.form['from'])
	a2 = int(request.form['to'])
	par = request.form['par']
	query = 'SELECT COUNT(*) FROM people where ' +str(par) + '>= ' +str(a1) + ' and ' +str(par) + '<=' +str(a2) 
	curs.execute(query)
	rows = curs.fetchall()
	listdata = []
	column = ['Range', 'Count']
	listdata.append(column)
	while a1 <= a2:
			q = 'SELECT COUNT(*) FROM people where ' +str(par) + ' >= ' +str(a1) + ' and ' +str(par) + ' <= ' + str(a1+0.5)
			print(q)
			curs.execute(q)
			rows = curs.fetchall()
			c = rows[0][0]
			st = str(a1) +' - '+ str(int(a1)+0.5)
			a1 = a1 + 0.5
			listdata.append([st,c])
	conn.close()
	return render_template('Bearth_success.html', data=listdata)	
"""	
@application.route('/Btitanic')
def titanic():
	return render_template('Btitanic.html')
"""
@application.route('/Btitanic_success', methods=['GET', 'POST'])
def Btitanic_success():	
	conn = sql.connect('titanic.db')
	curs = conn.cursor()
	#survived_male
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'male' and survived = 1 group by sex, survived, pclass")
	rows1 = curs.fetchall()
	mlistdata = []
	mlistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows1:
		pclass = 'Class' + str(i[0])
		count = i[1]
		mlistdata.append([pclass,count,"red"])
	#survived_female
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'female' and survived = 1 group by sex, survived, pclass")
	rows2 = curs.fetchall()
	flistdata = []
	flistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows2:
		pclass = 'Class' + str(i[0])
		count = i[1]
		flistdata.append([pclass,count,"blue"])
	#not_survived_male
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'male' and survived = 0 group by sex, survived, pclass")
	rows3 = curs.fetchall()
	nmlistdata = []
	nmlistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows3:
		pclass = 'Class' + str(i[0])
		count = i[1]
		nmlistdata.append([pclass,count,"green"])
	#not_survived_female
	curs.execute("Select pclass, COUNT(*) AS count from people where sex = 'male' and survived = 0 group by sex, survived, pclass")
	rows4 = curs.fetchall()
	nflistdata = []
	nflistdata.append(['Class','Count',{ role: 'style' }])
	for i in rows4:
		pclass = 'Class' + str(i[0])
		count = i[1]
		nflistdata.append([pclass,count,"yellow"])
	conn.close()
	return render_template('Btitanic_success.html', data1 = mlistdata, data2 = flistdata, data3 = nmlistdata, data4 = nflistdata)
	
if __name__ == "__main__":
	application.run()
	#app.run(host='0.0.0.0', port=port)


