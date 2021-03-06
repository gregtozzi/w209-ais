import altair as alt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import numpy as np
import math
import json


def base_map(df, color='#333333', dimensions=(560, 790), projection='mercator'):
    rendered_map = alt.Chart(df).mark_geoshape(color=color, strokeWidth=0).encode().project(
        type=projection,
    ).properties(
        width=dimensions[0],
        height=dimensions[1]
    )
    return rendered_map


def build_map(map_path):

    base_1 = gpd.read_file(map_path)

    base = base_map(base_1)

    locations = [['San Francisco', 37.78, -122.44, 0],
                 ['Oakland', 37.811816, -122.275828, 0],
                 ['Berkeley', 37.872645, -122.277138, 0],
                 ['Alameda', 37.77, -122.26, 28],
                 ['San Leandro', 37.726589, -122.148256,0],
                 ['Hayward', 37.668277, -122.101679,0],
                 ['Union City', 37.593332, -122.073275, 0],
                 ['Fremont', 37.548661, -122.002047,0],
                 ['Richmond', 37.936, -122.348282, 0],
                 ['Benicia', 38.07, -122.145650, 0],
                 ['San Mateo', 37.564227, -122.347733,0],
                 ['Redwood City', 37.484601, -122.253796,0],
                 ['Palo Alto', 37.441588, -122.155226,0],
                 ['Vallejo', 38.1, -122.25, 55],
                 ['Martinez', 38.014021, -122.145581, 0],
                 ['Tiburon', 37.89, -122.471, 45],
                 ['Bay Farm Isl.', 37.725, -122.22, 30]
                ]

    location_df = gpd.GeoDataFrame(
        {
            'lon': [x[2] for x in locations],
            'lat': [x[1] for x in locations],
            'name': [x[0] for x in locations],
            'angle': [x[3] for x in locations]
        }
    )


    city_base = alt.Chart(location_df).encode(longitude='lon', latitude='lat', text='name')

    city_layers = [
        city_base.transform_filter(alt.datum.name == name).mark_text(angle=angle, font='Gill Sans', color='grey') for (name, angle) in zip(location_df.name, location_df.angle)
    ]
    
    city_layers = alt.layer(*city_layers)


    bridges = [['Golden Gate', 37.825544, -122.479248],
               ['Golden Gate', 37.810238, -122.477471],
               ['Bay Bridge West', 37.789310, -122.387434],
               ['Bay Bridge West', 37.807916, -122.367529],
               ['Bay Bridge East', 37.814503, -122.359903],
               ['Bay Bridge East', 37.817503, -122.354686],
               ['Bay Bridge East', 37.818503, -122.352336],
               ['Bay Bridge East', 37.818986, -122.350373],
               ['Bay Bridge East', 37.821672, -122.331211],
               ['Bay Bridge East', 37.822019, -122.327145],
               ['Richmond-San Rafael', 37.942801, -122.479133],
               ['Richmond-San Rafael', 37.941143, -122.470174],
               ['Richmond-San Rafael', 37.939908, -122.465561],
               ['Richmond-San Rafael', 37.936752, -122.455369],
               ['Richmond-San Rafael', 37.936168, -122.453309],
               ['Richmond-San Rafael', 37.935660, -122.450702],
               ['Richmond-San Rafael', 37.935406, -122.448417],
               ['Richmond-San Rafael', 37.932674, -122.408188],
               ['Richmond-San Rafael', 37.932369, -122.404873],
               ['San Mateo Bridge', 37.573083, -122.263037],
               ['San Mateo Bridge', 37.590169, -122.244033],
               ['San Mateo Bridge', 37.624548, -122.131794],
               ['Dumbarton Bridge', 37.495561, -122.132929],
               ['Dumbarton Bridge', 37.499466, -122.128147],
               ['Dumbarton Bridge', 37.511852, -122.110428],
               ['Dumbarton Bridge', 37.522030, -122.102665],
               ['Dumbarton Bridge', 37.530088, -122.093356],
               ['Dumbarton Bridge', 37.532784, -122.087688],
               ['Dumbarton Bridge', 37.534916, -122.076658],
               ['Carquinez Bridge', 38.056094, -122.225308],
               ['Carquinez Bridge', 38.065179, -122.226084],
               ['Benicia Bridge', 38.048803, -122.128219],
               ['Benicia Bridge', 38.035514, -122.117658]
              ]

    bridges = gpd.GeoDataFrame(bridges, columns=['Name', 'LAT', 'LON'])
    bridge_points = [Point(xy) for xy in zip(bridges.LON, bridges.LAT)]
    bridges['geometry'] = bridge_points
    bridges = bridges.groupby(['Name'])['geometry'].apply(lambda x: LineString(x.tolist()))
    bridges = gpd.GeoDataFrame(bridges)
    bridge_map = alt.Chart(bridges).mark_geoshape(filled=False,
                                                  color='white',
                                                  strokeWidth=1.25)

    min_lat = 37.415
    max_lat_text = 38.15881855030604
    max_lat = 38.115
    lat_inc = 0.1

    min_lon_text = -122.593
    min_lon = -122.548
    max_lon = -121.9382
    lon_inc = 0.1

    lat_lines  = []
    lat_labels = []
    lon_lines  = []
    lon_labels = []

    for i in np.arange(math.ceil(min_lat/lat_inc)*lat_inc, math.floor((max_lat)/lat_inc)*lat_inc, lat_inc):
        j = round(i, 1)
        name = str(abs(j))+"°N"
        val1 = [name, j, min_lon]
        val2 = [name, j, max_lon]
        #val3 = [name, j+0.008, min_lon+0.02]
        val3 = [name, j, min_lon_text+0.02]
        lat_lines.append(val1)
        lat_lines.append(val2)
        lat_labels.append(val3)

    lat_lines = gpd.GeoDataFrame(lat_lines, columns=['Name', 'LAT', 'LON'])
    lat_lines_pts = [Point(xy) for xy in zip(lat_lines.LON, lat_lines.LAT)]
    lat_lines['geometry'] = lat_lines_pts
    latitudes = lat_lines.groupby(['Name'])['geometry'].apply(lambda x: LineString(x.tolist()))
    latitudes = gpd.GeoDataFrame(latitudes)

    for i in np.arange(math.ceil(min_lon/lon_inc)*lon_inc, math.floor((max_lon + lon_inc)/lon_inc)*lon_inc, lon_inc):
        j = round(i, 1)
        name = str(abs(j))+"°W"
        val1 = [name, min_lat, j]
        val2 = [name, max_lat, j]
        #val3 = [name, max_lat-0.018, j-0.01]
        val3 = [name, max_lat_text-0.025, j]
        lon_lines.append(val1)
        lon_lines.append(val2)
        lon_labels.append(val3)

    lon_lines = gpd.GeoDataFrame(lon_lines, columns=['Name', 'LAT', 'LON'])
    lon_lines_pts = [Point(xy) for xy in zip(lon_lines.LON, lon_lines.LAT)]
    lon_lines['geometry'] = lon_lines_pts
    longitudes = lon_lines.groupby(['Name'])['geometry'].apply(lambda x: LineString(x.tolist()))
    longitudes = gpd.GeoDataFrame(longitudes)

    lat_map = alt.Chart(latitudes).mark_geoshape(filled=False,
                                                 color='grey',
                                                 strokeWidth=1.25,
                                                 strokeDash=[1, 2])
    lon_map = alt.Chart(longitudes).mark_geoshape(filled=False,
                                                  color='grey',
                                                  strokeWidth=1.25,
                                                  strokeDash=[1, 2])
    lat_labels = pd.DataFrame(lat_labels, columns=['Name', 'LAT', 'LON'])
    lat_annotations = alt.Chart(lat_labels).encode(text='Name:N',
                                                   latitude='LAT',
                                                   longitude='LON').mark_text(angle=0, font='Gill Sans', color = 'grey')

    lon_labels = pd.DataFrame(lon_labels, columns=['Name', 'LAT', 'LON'])
    lon_annotations = alt.Chart(lon_labels).encode(text='Name:N',
                                                   latitude='LAT',
                                                   longitude='LON').mark_text(angle=270, font='Gill Sans', color = 'grey')
    
    water_labels = [['Treas. Island', 37.839455, -122.376198, 0],
                    ['San Pablo Bay', 38.064760, -122.39, 0],
                    #['Napa River',38.115239, -122.277615,60],
                    ['San Francisco Bay', 37.65, -122.275, 0],
                    ['Suisun Bay', 38.0782, -122.0724, 0]
                   ]

    water_location_df = gpd.GeoDataFrame({
        'lon': [x[2] for x in water_labels],
        'lat': [x[1] for x in water_labels],
        'name': [x[0] for x in water_labels],
        'angle': [x[3] for x in water_labels]
    })

    water_base = alt.Chart(water_location_df).encode(longitude='lon', latitude='lat', text='name')

    water_layers = [
        water_base.transform_filter(alt.datum.name == name).mark_text(angle=angle, font='Gill Sans', color='lightgrey')
        for (name, angle) in zip(water_location_df.name, water_location_df.angle)
    ]
    
    water_layers = alt.layer(*water_layers)

    final_chart = alt.layer(base, bridge_map, lat_map, lon_map, lat_annotations,
                            lon_annotations, city_layers, water_layers)
    return final_chart


def vsl_map(vsl_path, map_path, output_path=None):
    """
    Given input files to define the map's geography and
    location of vessels, return a map.
    
    Args:
        vsl_path: str giving the path to the vessel CSV
                  file
        map_path: str giving the path to the base map's
                  topojson file
                  
    Returns:
        alt.Chart
    """
    # Build the base map
    base_map = build_map(map_path)
    
    # Read the vessel data
    df = gpd.read_file(vsl_path, GEOM_POSSIBLE_NAMES='geometry', KEEP_GEOM_COLUMNS='NO')
    
    # Define Altair selections
    selection    = alt.selection_multi(fields=['Speed', 'Length'])
    day_select   = alt.selection_multi(fields=['Day'])
    route_select = alt.selection_multi(on='click', fields=['Route'])

    # Define color conditions
    color = alt.condition(
        selection,
        alt.value('orange'),
        alt.value('lightgray')
    )
    
    day_color = alt.condition(
        day_select,
        alt.value('orange'),
        alt.value('lightgray')
    )
    
    route_color = alt.condition(
        route_select,
        alt.value('orange'),
        alt.value('lightgray')
    )

    # Define opacity condition associated with the route selection
    opacity = alt.condition(
        route_select,
        alt.value(0.25),
        alt.value(0.005)
    )
    
    # Build the actual map
    vessel_map = alt.Chart(df).mark_geoshape(
        filled=False,
        color='orange',
        strokeWidth=1
    ).encode(
        opacity=opacity,
        color=route_color,
        tooltip='Route'
    ).transform_filter(
        selection
    ).transform_filter(
        day_select
    ).add_selection(
        route_select
    )
    
    # Build the rectangular speed/length select pad
    legend = alt.Chart(
        df
    ).mark_rect(
        strokeWidth=1,
        stroke='white'
    ).encode(
        y=alt.Y('Speed:O', axis=alt.Axis(orient='right')),
        x=alt.X('Length:O', axis=alt.Axis(orient='top')),
        color=color
    ).add_selection(
        selection
    )
    
    # Build the bar chart of transits by day
    # TODO: this currently drops days that aren't shown.  I'd prefer
    # that it zeroed them out but didn't drop them    
    day_hist = alt.Chart(
        df
    ).mark_bar(
    ).encode(
        color=day_color,
        y=alt.Y(
            'Day:N',
            sort=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            axis=alt.Axis(orient='right')),
        x=alt.X('Transits:Q')
    ).transform_filter(
        selection
    ).transform_filter(
        route_select
    ).transform_aggregate(
        Transits='sum(Count)',
        groupby=['Day']
    ).add_selection(
        day_select
    ).properties(
        width=80,
        height=100
    )
    
    route_hist = alt.Chart(df).mark_bar().encode(
        y=alt.Y(
            'Route:N',
            axis=alt.Axis(orient='right'),
            sort='-x'
        ),
        x='Transits:Q',
        color=route_color
    ).transform_filter(
        selection
    ).transform_filter(
        day_select
    ).transform_aggregate(
        Transits='sum(Count)',
        groupby=['Route']
    ).transform_window(
        rank='rank(Transits)',
        sort=[alt.SortField('Transits', order='descending')]
    ).transform_filter(
        (alt.datum.rank < 16)
    ).add_selection(
        route_select
    ).properties(
        width=80,
    )
    
    # The combined map is a combination of the visualizations
    # described above
    combined_map = base_map + vessel_map | (day_hist & legend & route_hist)
    
    if output_path:
        with open(output_path, 'w') as jsonfile:
            json.dump(combined_map.to_json(), jsonfile)
    
    return combined_map