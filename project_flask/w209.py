from flask import Flask, render_template
import geopandas as gpd
import altair as alt

app = Flask(__name__)

base_map_df = gpd.read_file("static/data/small_bay_topo.json")

base_map = alt.Chart(base_map_df).mark_geoshape(
	color="#333333", strokeWidth=0
	).encode().project(
        type='mercator', 
    ).properties(
        width=560,
        height=800
    )

base_map_json = base_map.to_json()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getMap')
def getMap():
	return base_map_json