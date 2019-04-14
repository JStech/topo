var camera, controls, scene, renderer, elevator;

function init() {

  scene = new THREE.Scene();
  scene.background = new THREE.Color( 0x888888 );
  scene.fog = new THREE.FogExp2( 0x888888, 0.0002 );

  renderer = new THREE.WebGLRenderer( { antialias: true } );
  renderer.setPixelRatio( window.devicePixelRatio );
  var w = document.getElementById('model').clientWidth;
  var h = document.getElementById('model').clientHeight;
  renderer.setSize(w, h);
  document.getElementById('model').appendChild( renderer.domElement );

  camera = new THREE.PerspectiveCamera( 30, w/h, 1, 1000 );
  camera.position.set( 100, 70, 80 );

  // controls
  controls = new THREE.OrbitControls( camera, renderer.domElement );

  //controls.addEventListener( 'change', render ); // call this only in static scenes (i.e., if there is no animation loop)

  controls.enableDamping = true; // an animation loop is required when either damping or auto-rotation are enabled
  controls.dampingFactor = 0.25;

  controls.screenSpacePanning = false;

  controls.minDistance = 20;
  controls.maxDistance = 500

  controls.maxPolarAngle = Math.PI / 2;

  // lights

  var pointLights = [
    new THREE.PointLight( 0xdddddd, 0.6),
    new THREE.PointLight( 0xccdddd, 0.6),
    new THREE.PointLight( 0x8899bb, 0.6),
  ];

  pointLights[0].position.set( 0, 100, 50 );
  scene.add(pointLights[0]);

  pointLights[1].position.set( 50, 100, -50 );
  scene.add(pointLights[1]);

  pointLights[2].position.set( -50, 100, -50 );
  scene.add(pointLights[2]);

  var ambientLight = new THREE.AmbientLight(0x111111);
  scene.add(ambientLight);
  //

  window.addEventListener( 'resize', onWindowResize, false );
}

function fetchElev() {
  var w = document.getElementById('width').value;
  var h = document.getElementById('height').value;
  var x_max = Math.floor(20 * w/h);
  var y_max = Math.floor(20 * h/w);
  locations = [];
  var i=0;
  var x_vals = [];
  var y_vals = [];
  var v = [{}, {}, {}, {}];
  v[0].lat = parseFloat(document.getElementById('lat1').innerHTML);
  v[0].lng = parseFloat(document.getElementById('lng1').innerHTML);
  v[1].lat = parseFloat(document.getElementById('lat2').innerHTML);
  v[1].lng = parseFloat(document.getElementById('lng2').innerHTML);
  v[2].lat = parseFloat(document.getElementById('lat3').innerHTML);
  v[2].lng = parseFloat(document.getElementById('lng3').innerHTML);
  v[3].lat = parseFloat(document.getElementById('lat4').innerHTML);
  v[3].lng = parseFloat(document.getElementById('lng4').innerHTML);

  for (var x=0; x<=x_max; x++) {
    x_vals[x] = x - x_max/2;
  }
  for (var y=0; y<=y_max; y++) {
    y_vals[y] = y - y_max/2;
  }

  for (var x=0; x<=x_max; x++) {
    for (var y=0; y<=y_max; y++) {
      var lat = (x*y*v[0].lat + x*(y_max-y)*v[3].lat + (x_max-x)*y*v[1].lat +
        (x_max-x)*(y_max-y)*v[2].lat)/(x_max*y_max)
      var lng = (x*y*v[0].lng + x*(y_max-y)*v[3].lng + (x_max-x)*y*v[1].lng +
        (x_max-x)*(y_max-y)*v[2].lng)/(x_max*y_max)
      locations[i] = {lat: lat, lng: lng};
      i++;
    }
  }

  num_elev_calls = Math.ceil(locations.length/400);
  var i=0;
  var stop = false;
  function elevCallLoop() {
    var t=i;
    elevator.getElevationForLocations({'locations': locations.slice(i, i+400)},
      function(results, status) {
        console.log(status);
        if (status === 'OK') {
          makeModel(results, x_vals, y_vals, t);
        } else if (status == 'OVER_QUERY_LIMIT') {
          stop = true;
        } else {
          console.log(status);
        }
      });
    if (i+400<locations.length && !stop) {
      setTimeout(elevCallLoop, 1000);
    }
    i += 400;
  };
  elevCallLoop();
}

var elev = [];
function makeModel(results, x_vals, y_vals, start) {
  var i;
  for (i=0; i<results.length; i++) {
    elev[i+start] = results[i].elevation;
  }
  num_elev_calls--;
  if (num_elev_calls > 0) {
    return;
  }

  var max_elev = Math.max.apply(Math, elev);
  var min_elev = Math.min.apply(Math, elev);

  console.log(max_elev, min_elev);
  for (i=0; i<elev.length; i++) {
    elev[i] = 10*(elev[i] - min_elev)/(max_elev - min_elev) + 5;
  }
  // mountain
  scene.remove(scene.getObjectByName('model'));
  var geometry = makeMesh(x_vals, y_vals, elev);
  var material = new THREE.MeshPhongMaterial({color: 0xdddddd, flatShading: false});
  var mesh = new THREE.Mesh( geometry, material );
  mesh.name = 'model';
  mesh.position.x = 0;
  mesh.position.y = 0;
  mesh.position.z = 0;
  mesh.updateMatrix();
  mesh.matrixAutoUpdate = false;
  scene.add( mesh );
  return false;
}

function onWindowResize() {
  var w = document.getElementById('model').clientWidth;
  var h = document.getElementById('model').clientHeight;
  camera.aspect = w/h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}

function animate() {
  requestAnimationFrame( animate );
  controls.update(); // only required if controls.enableDamping = true, or if controls.autoRotate = true
  render();
}

function render() {
  renderer.render( scene, camera );
}

function makeMesh(x_values, y_values, z_values) {
  var geometry = new THREE.Geometry();
  var i=0, i_x, i_y;
  var l_x = x_values.length;
  var l_y = y_values.length;
  var N = l_x * l_y;

  // draw surface
  for (i_x = 0; i_x < l_x; i_x++) {
    for (i_y = 0; i_y < l_y; i_y++, i++) {
      geometry.vertices.push(
        new THREE.Vector3(y_values[i_y], z_values[i], x_values[i_x])
      );
      if (i_x > 0 && i_y > 0) {
        geometry.faces.push(
          new THREE.Face3(i, i-1-l_y, i-1),
          new THREE.Face3(i, i-l_y, i-1-l_y)
        );
      }
    }
  }

  // draw sides
  var last_i_x = 0;
  var last_i_y = 0;
  geometry.vertices.push(new THREE.Vector3(y_values[0], 0, x_values[0]));
  i_x = 0;
  for (i = 1; i < l_y; i++) {
    i_y = i;
    geometry.vertices.push(new THREE.Vector3(y_values[i_y], 0, x_values[i_x]));
    geometry.faces.push(
      new THREE.Face3(N+i-1, l_y*i_x+i_y, N+i),
      new THREE.Face3(N+i-1, l_y*last_i_x+last_i_y, l_y*i_x+i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }
  for (i = 0; i < l_x; i++) {
    i_x = i;
    geometry.vertices.push(new THREE.Vector3(y_values[i_y], 0, x_values[i_x]));
    geometry.faces.push(
      new THREE.Face3(N+l_y+i-1, l_y*i_x+i_y, N+l_y+i),
      new THREE.Face3(N+l_y+i-1, l_y*last_i_x+last_i_y, l_y*i_x+i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }
  for (i = 0; i < l_y; i++) {
    i_y = l_y - i - 1;
    geometry.vertices.push(new THREE.Vector3(y_values[i_y], 0, x_values[i_x]));
    geometry.faces.push(
      new THREE.Face3(N+l_y+l_x+i-1, l_y*i_x+i_y, N+l_y+l_x+i),
      new THREE.Face3(N+l_y+l_x+i-1, l_y*last_i_x+last_i_y, l_y*i_x+i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }
  for (i = 0; i < l_x; i++) {
    i_x = l_x - i - 1;
    geometry.vertices.push(new THREE.Vector3(y_values[i_y], 0, x_values[i_x]));
    geometry.faces.push(
      new THREE.Face3(N+2*l_y+l_x+i-1, l_y*i_x+i_y, N+2*l_y+l_x+i),
      new THREE.Face3(N+2*l_y+l_x+i-1, l_y*last_i_x+last_i_y, l_y*i_x+i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }

  geometry.computeVertexNormals(true);
  return geometry;
}
