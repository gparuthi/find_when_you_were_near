from datetime import date, datetime, timedelta
from flask import Flask, url_for, request, session, redirect, render_template, make_response, current_app, jsonify
from logger import logger
import datetime, random, numpy as np, pandas as pd
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from werkzeug.contrib.fixers import ProxyFix
import os
import css

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'kml'])

''' Flask Server'''
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.wsgi_app = ProxyFix(app.wsgi_app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse_kml(filename):
    """Parses a KML file into a Pandas DataFrame"""
    with open(filename) as f:
        rows = []
        soup = BeautifulSoup(f)
        for time, coords in zip(soup.findAll('when'), soup.findAll('gx:coord')):
            timestamp = time.string
            coords = coords.string.split(' ')[:2]
            latitude = float(coords[0])
            longitude = float(coords[1])
            rows.append([timestamp, latitude, longitude])
        df = pd.DataFrame(rows, columns=['Timestamp', 'Longitude', 'Latitude'])
        df['Timestamp'] = pd.to_datetime(df.Timestamp)
        return df

def get_close_to(df, loc, radius):
    """Only look at data within 1 miles of the locs latitude and longitude."""
    miles = radius
    degrees = miles / 69.11
    for col in ('Latitude', 'Longitude'):
        median = loc[col]
        df = df[(df[col] >= median - degrees) & (df[col] <= median + degrees)]
    return df


def get_locs(filename, latitude, longitude, radius=0.01):
	df = parse_kml(filename)
	loc = {'Latitude': float(latitude), 'Longitude':float(longitude)} #42.2802209, -83.7513823
	df2 = get_close_to(df, loc, radius)
	return df2

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # post request
        file = request.files['file']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        print request.form.get('isjson','False')
        isjson =  True if request.form.get('isjson','False')=='true' else False
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'])
            #print (path)
            #assign to the right folder based on the device id
            if not os.path.exists(path):
                logr.plog("the folder does not exist, create one" ,class_name= "/")
                os.makedirs(path)
            path  = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            df = get_locs(path, latitude, longitude)
            file.save(path)
            if isjson: 
                return jsonify({'data':df.to_dict(outtype='records')})
            else:
                # return render_template('hits.html', data=alldata)
                html = df.to_html(bold_rows=False)
                return '''
                <!doctype html>
                <title>Results</title>
                <head><style>%s</style></head>
                <body>
                <h1>Here are the timestamps when you were close to the given location</h1>
                %s
                </body>
                '''%(css.table_css, html)

    return '''
    <!doctype html>
    <head><style>%s</style></head>
    <title>Find out when you were close to a given location</title>
    <h1>Find out when you were close to a given location:</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p>Choose a .KML file: <input type=file name=file></input><br />
      	Latitude: <input type=text name=latitude > <br />
      	Longitude: <input type=text name=longitude /> <br />
        JSON Output: <input id="isjson" name="isjson" value="true" type="checkbox"><br />
        <input type=submit value=Upload> 
         </p>
    </form>
    '''%(css.table_css)

if __name__ == '__main__':
    #init logger
    logr = logger('./Logs','location_time_finder_dev')
    app.run(
        host="0.0.0.0",
        debug=True,
        port = 15000#, ssl_context=('keys/ssl.crt','keys/ssl.key')
        )  
else:
    #init logger
    logr = logger('./Logs','location_time_finder')