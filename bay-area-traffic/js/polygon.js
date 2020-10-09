d3.json("data/sf_bay.geojson", function(data) {
  // Build the map
  var map = L.map('map')
    /* Make sure that the map encompassess all of the points.
    Using fitBounds, there's no need to set the initial
    position or zoom for the map. */
    .fitBounds(L.geoJson(data)
      .getBounds());

  // Add the base map
  var mapLink = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  // Add an SVG layer to the map
  L.svg({clickable:true}).addTo(map);
  const overlay = d3.select(map.getPanes().overlayPane);
  const svg = overlay.select('svg')
    .attr("pointer-events", "auto");

  // Add the points to the SVG layer
  var Squares = svg.selectAll('rect')
  	.attr("class", "Squares")
  	.data(data.features)
  	.enter()
  	.append('rect')
  	.attr("fill", "red")
  	// Leaflet converts the lat and lon to a value that D3 can plot
  	.attr("x", d => map.latLngToLayerPoint([d.geometry.coordinates[1],d.geometry.coordinates[0]]).x)
  	.attr("y", d => map.latLngToLayerPoint([d.geometry.coordinates[1],d.geometry.coordinates[0]]).y)
  	.attr("width", 3)
  	.attr("height", 3)
    .style("opacity", 0.1);

  // Set up an update so the points remain in place when zooming
  const update = () => Squares
  	.attr("x", d => map.latLngToLayerPoint([d.geometry.coordinates[1],d.geometry.coordinates[0]]).x)
    .attr("y", d => map.latLngToLayerPoint([d.geometry.coordinates[1],d.geometry.coordinates[0]]).y)
  map.on("zoomend", update);
});

/* TODO:
1.  DONE: Zoom doesn't work properly.  Look here https://observablehq.com/@sfu-iat355/intro-to-leaflet-d3-interactivity
    for the fix.  Likely using deprecated code following L.svg()...
2.  Rebuild my data and plot it
3.  Make the color interpolation work
3.  Set an acceptable zoom range
4.  Disable panning
5.  Interactivity
6.  Make this work in D3 v6
*/