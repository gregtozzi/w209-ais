from flask import Flask, render_template
import numpy as np
import geopandas as gpd
import altair as alt
from map_builder.build_map import build_map

app = Flask(__name__)

#base_map_df = gpd.read_file("static/data/small_bay_topo.json")
vessels = gpd.read_file('static/data/bay_traffic.csv', GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")

"""
vessels['max_SOG'] = vessels['max_SOG'].astype(float)
vessels_LOA = vessels.LOA.to_numpy()
vessels_LOA[vessels_LOA == ''] = '0'
vessels.LOA = vessels_LOA.astype(float)

speed = np.repeat('10-20kt', vessels.shape[0])
speed[vessels.max_SOG > 20] = '20-30kt'
speed[vessels.max_SOG > 30] = '>30kt'
speed[vessels.max_SOG <= 10] = '0-10kt'
vessels['Speed'] = speed

Length = np.repeat('100-200m', vessels.shape[0])
Length[vessels.LOA >= 200] = '200-300m'
Length[vessels.LOA >= 300] = '>300m'
Length[vessels.LOA < 100] = '0-100m'
vessels['Length'] = Length
"""

selection = alt.selection_multi(fields=['Speed', 'Length'])

color = alt.condition(selection,
                      alt.value('orange'),
                      alt.value('lightgray'))

opacity = alt.condition(selection, alt.value(0.03), alt.value(0))


# base_map = alt.Chart(base_map_df).mark_geoshape(
# 	color="#333333", strokeWidth=0
# 	).encode().project(
#         type='mercator',
#     ).properties(
#         width=560,
#         height=800
#     )

base_map = build_map()


vessel_map = alt.Chart(vessels).mark_geoshape(filled=False,
                                              color='orange',
                                              strokeWidth=1).encode(opacity=opacity)

legend = alt.Chart(vessels).mark_rect().encode(
    y=alt.Y('Speed:O', axis=alt.Axis(orient='right')),
    x='Length:O',
    color=color
).add_selection(
    selection
)

map_json = (base_map + vessel_map | legend).to_json()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getMap')
def getMap():
	return map_json
