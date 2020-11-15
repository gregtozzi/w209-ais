document.dayForm.onclick = function(){
    var day = document.querySelector('input[name = day]:checked').value;
    var spec = "http://127.0.0.1:5000/getMap/" + day;
    vegaEmbed('#vis', spec).then(function(result) {}).catch(console.error);
}

var spec = "http://127.0.0.1:5000/getMap/Mon";
vegaEmbed('#vis', spec).then(function(result) {}).catch(console.error);