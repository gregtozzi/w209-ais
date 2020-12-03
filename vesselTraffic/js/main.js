var spec = "../data/sf_bay.json";
//var spec = "https://people.ischool.berkeley.edu/~greg.tozzi/vesselTraffic/data/sf_bay.json";
vegaEmbed('#vis', spec).then(function(result) {}).catch(console.error);