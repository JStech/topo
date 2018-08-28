if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var camera, controls, scene, renderer;

function init() {

  scene = new THREE.Scene();
  scene.background = new THREE.Color( 0xcccccc );
  scene.fog = new THREE.FogExp2( 0xcccccc, 0.002 );

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

  controls.minDistance = 100;
  controls.maxDistance = 500

  controls.maxPolarAngle = Math.PI / 2;

  // world
  var geometry = makeMesh([-6, -2, 2, 6], [-10, -5, 0, 5, 10],
    [16, 6, 7, 10, 15, 18, 0, 19, 0, 19, 7, 14, 5, 18, 6, 7, 10, 9, 11, 9]);

  var material = new THREE.MeshPhongMaterial( { color: 0xffffff, flatShading: true } );

  var mesh = new THREE.Mesh( geometry, material );
  mesh.position.x = 0;
  mesh.position.y = 0;
  mesh.position.z = 0;
  mesh.updateMatrix();
  mesh.matrixAutoUpdate = false;
  scene.add( mesh );

  // lights

  var light = new THREE.DirectionalLight( 0xffffff );
  light.position.set( 1, 1, 1 );
  scene.add( light );

  var light = new THREE.DirectionalLight( 0x002288 );
  light.position.set( - 1, - 1, - 1 );
  scene.add( light );

  var light = new THREE.AmbientLight( 0x222222 );
  scene.add( light );

  //

  window.addEventListener( 'resize', onWindowResize, false );
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
        new THREE.Vector3(x_values[i_x], z_values[i], y_values[i_y])
      );
      if (i_x > 0 && i_y > 0) {
        geometry.faces.push(
          new THREE.Face3(i, i-1, i-1-l_y),
          new THREE.Face3(i, i-1-l_y, i-l_y)
        );
      }
    }
  }

  // draw sides
  var last_i_x = 0;
  var last_i_y = 0;
  geometry.vertices.push(new THREE.Vector3(x_values[0], 0, y_values[0]));
  i_x = 0;
  for (i = 1; i < l_y; i++) {
    i_y = i;
    geometry.vertices.push(new THREE.Vector3(x_values[i_x], 0, y_values[i_y]));
    geometry.faces.push(
      new THREE.Face3(N+i-1, N+i, l_y*i_x+i_y),
      new THREE.Face3(N+i-1, l_y*i_x+i_y, l_y*last_i_x+last_i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }
  for (i = 0; i < l_x; i++) {
    i_x = i;
    geometry.vertices.push(new THREE.Vector3(x_values[i_x], 0, y_values[i_y]));
    geometry.faces.push(
      new THREE.Face3(N+l_y+i-1, N+l_y+i, l_y*i_x+i_y),
      new THREE.Face3(N+l_y+i-1, l_y*i_x+i_y, l_y*last_i_x+last_i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }
  for (i = 0; i < l_y; i++) {
    i_y = l_y - i - 1;
    geometry.vertices.push(new THREE.Vector3(x_values[i_x], 0, y_values[i_y]));
    geometry.faces.push(
      new THREE.Face3(N+l_y+l_x+i-1, N+l_y+l_x+i, l_y*i_x+i_y),
      new THREE.Face3(N+l_y+l_x+i-1, l_y*i_x+i_y, l_y*last_i_x+last_i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }
  for (i = 0; i < l_x; i++) {
    i_x = l_x - i - 1;
    geometry.vertices.push(new THREE.Vector3(x_values[i_x], 0, y_values[i_y]));
    geometry.faces.push(
      new THREE.Face3(N+2*l_y+l_x+i-1, N+2*l_y+l_x+i, l_y*i_x+i_y),
      new THREE.Face3(N+2*l_y+l_x+i-1, l_y*i_x+i_y, l_y*last_i_x+last_i_y),
    );
    last_i_y = i_y;
    last_i_x = i_x;
  }

  return geometry;
}
