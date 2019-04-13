var map;
function initMap() {
  elevator = new google.maps.ElevationService;
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 40.255, lng: -105.62},
    zoom: 12
  });
  map.setMapTypeId('terrain');
  drawBox();
  map.addListener('center_changed', updateBox);
}

var box;
function drawBox() {
  var boxCoords = [
    {lat: +0.01, lng: +0.01},
    {lat: +0.01, lng: -0.01},
    {lat: -0.01, lng: -0.01},
    {lat: -0.01, lng: +0.01}];
  box = new google.maps.Polygon({
    paths: boxCoords,
    strokeColor: '#0000FF',
    strokeOpacity: 0.6,
    strokeWeight: 5,
    fillColor: '#0000FF',
    fillOpacity: 0.3
  });
  box.setMap(map);
  updateBox();
}

function updateBox() {
  var miles_per_deg = 69.172;
  var cen = map.getCenter();
  var w = document.getElementById('width').value / miles_per_deg / 2;
  var h = document.getElementById('height').value / miles_per_deg / 2;
  var theta = -document.getElementById('angle').value * Math.PI / 180.;
  var s = Math.sin(theta);
  var c = Math.cos(theta);
  var cos_lat = Math.cos(cen.lat() * Math.PI / 180.);
  var boxCoords = [
    {lat: cen.lat()+ h*c+w*s, lng: cen.lng()+(-h*s+w*c)/cos_lat},
    {lat: cen.lat()+ h*c-w*s, lng: cen.lng()+(-h*s-w*c)/cos_lat},
    {lat: cen.lat()+-h*c-w*s, lng: cen.lng()+( h*s-w*c)/cos_lat},
    {lat: cen.lat()+-h*c+w*s, lng: cen.lng()+( h*s+w*c)/cos_lat}];
  box.setPath(boxCoords);
  document.getElementById('lat1').innerHTML = boxCoords[0].lat;
  document.getElementById('lng1').innerHTML = boxCoords[0].lng;
  document.getElementById('lat2').innerHTML = boxCoords[1].lat;
  document.getElementById('lng2').innerHTML = boxCoords[1].lng;
  document.getElementById('lat3').innerHTML = boxCoords[2].lat;
  document.getElementById('lng3').innerHTML = boxCoords[2].lng;
  document.getElementById('lat4').innerHTML = boxCoords[3].lat;
  document.getElementById('lng4').innerHTML = boxCoords[3].lng;
}

