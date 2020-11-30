from flask import Flask, render_template
import numpy as np
import geopandas as gpd
import altair as alt
from map_builder.build_map import vsl_map

app = Flask(__name__)

vessels = gpd.read_file('static/data/transits.csv', GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")

Mon = vsl_map(vessels[vessels.day == 'Mon'])
Tue = vsl_map(vessels[vessels.day == 'Tue'])
Wed = vsl_map(vessels[vessels.day == 'Wed'])
Thu = vsl_map(vessels[vessels.day == 'Thu'])
Fri = vsl_map(vessels[vessels.day == 'Fri'])
Sat = vsl_map(vessels[vessels.day == 'Sat'])
Sun = vsl_map(vessels[vessels.day == 'Sun'])

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getMap/Mon')
def getMon():
	return Mon

@app.route('/getMap/Tue')
def getTue():
  return Tue

@app.route('/getMap/Wed')
def getWed():
  return Wed

@app.route('/getMap/Thu')
def getThu():
  return Thu

@app.route('/getMap/Fri')
def getFri():
  return Fri

@app.route('/getMap/Sat')
def getSat():
  return Sat

@app.route('/getMap/Sun')
def getSun():
  return Sun

