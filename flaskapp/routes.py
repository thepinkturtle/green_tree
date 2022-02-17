""" routes.py - Flask route definitions

Flask requires routes to be defined to know what data to provide for a given
URL. The routes provided are relative to the base hostname of the website, and
must begin with a slash."""
from flaskapp import app
from flask import render_template, request, jsonify
from wrangling_scripts.wrangling import data_wrangling, username, find_shortest_path
import json

limit = 10 # Pass in this to the data_wrangling() function below if you only want to visualize a few points
data, n = data_wrangling()

# The following two lines define two routes for the Flask app, one for just
# '/', which is the default route for a host, and one for '/index', which is
# a common name for the main page of a site.
#
# Both of these routes provide the exact same data - that is, whatever is
# produced by calling `index()` below.
@app.route('/')
@app.route('/index.html')
def index():
    """Renders the index.html template"""
    # Renders the template (see the index.html template file for details). The
    # additional defines at the end (data, n) are the variables
    # handed to Jinja while it is processing the template.
    return render_template('index.html', 
    						data=data, n=n)

@app.route('/summary_stats.html')
def summary():
	return render_template('summary_stats.html',
	data=data, n=n)

@app.route('/output/all_value_added-10000.csv')
def data_fetch():
	return render_template('output/all_value_added-10000.csv', data=data, n=n)

@app.route('/compute_shortest_path')
def compute_shortest_path():
	station1 = request.args.get('station1')
	station2 = request.args.get('station2')
	carRange = request.args.get('range')
	objective = request.args.get('objective')

	station1 = int(station1)
	station2 = int(station2)
	carRange = int(carRange)
	objective = int(objective)

	nodes_on_path, str_of_path, cost_of_path, edges_on_path, total_distance, number_of_stops = find_shortest_path(station1, station2, carRange, objective)
	
	return json.dumps([nodes_on_path, str_of_path, cost_of_path, edges_on_path, total_distance, number_of_stops])