# Visualizing San Francisco Bay Vessel Traffic

#### [Greg Tozzi](https://www.linkedin.com/in/gregorytozzi/) | Emma Tebbe | Joanna Wang | December, 2020

### [View the Visualization](https://gregtozzi.com/w209-ais/)

*This is our project from the [data visualization](https://www.ischool.berkeley.edu/courses/datasci/209) course that we took as part of the UC Berkeley School of Information's [Master of Information and Data Science](https://datascience.berkeley.edu) program.  Using massive datasets made available by the [National Oceanographic and Atmospheric Administration and the Bureau of Ocean Energy Management](https://marinecadastre.gov/ais/), we developed a bespoke interactive visualization of vessel traffic in San Francisco Bay.*

**EDA and Prototyping**.  We conducted EDA for this project in [Tableau](https://public.tableau.com/profile/greg.tozzi#!/vizhome/vessels_underway_sf_bay_by_day_and_length/CountofVesselsUnderway) and also used Tableau for early [prototyping](https://public.tableau.com/profile/greg.tozzi#!/vizhome/vessel_density_by_length/Sheet1).

We ran through several iterations of the map design beginning with simple Matplotlib plots and moving on to D3 and D3 with Leaflet.  Samples of these are shown  below.

![Iterations](https://github.com/gregtozzi/w209-ais/blob/main/images/iteration.png)

In the end, we liked the clean presentation offered by a custom base map constructed in Mapshaper with basic annotations.  We also appreciated the ability to iterate in a notebook environment offered by the Altair/Vega-Lite stack.  The final form of our map is shown below.

![Final map](https://github.com/gregtozzi/w209-ais/blob/main/images/final_map.png)

**Route Clustering**.  We rely on substantial backend processing in Python to prepare the data for the visualization.  A particularly interesting challenge was clustering routes.  We developed a greedy clustering algorithm that first compared bounding box similarities and then computed the Hausdorff distance for candidate routes.  This resulted in clusters like those shown below.  We then curated these clusters to arrive at the final groupings presented in the visualization.

![Clusters](https://github.com/gregtozzi/w209-ais/blob/main/images/route_clusters.png)

Our final design was informed by several structured and recorded user tests during which we presented professional mariners with specific tasks to perform and observed their interaction with the visualization.  We then applied the MoSCoW method to prioritize improvements.

**Skills demonstrated:** *Visualization* | *User Testing* | *MoSCoW* | *Geospatial Analysis* | *Design of Interactions* | *Deployment to the Web*

**Languages and frameworks**: *Python* | *Tableau* | *Altair* | *Vega-Lite* | *Mapshaper* | *Geopandas* | *Shapely* | *Flask* | *HTML/CSS* | *D3* | *Leaflet* | *Javascript*
