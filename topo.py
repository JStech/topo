#!/usr/bin/env python3
from collections import defaultdict
import configparser
import itertools
import json
import math
import sys
import time
import urllib.parse
import urllib.request

if len(sys.argv) != 2:
  print("Usage: {} topo_config_file.conf".format(sys.argv[0]), file=sys.stderr)
  exit(1)

# Parse config file
topoconfig = configparser.ConfigParser()
topoconfig.read(sys.argv[1])

api_key = topoconfig['Gmaps']['APIkey']

box = list(map(float, topoconfig['Input']['box'].split()))
box = [(box[2*i], box[2*i+1]) for i in range(4)]

if 'mode' not in topoconfig['Output']:
  print("Output mode not specified. Defaulting to 3d model")
  mode = "3d"
else:
  mode = topoconfig['Output']['mode']

if 'file' not in topoconfig['Output']:
  print("Output file not specified. Defaulting to `topo.stl'.")
  out_file = 'topo.stl'
else:
  out_file = topoconfig['Output']['file']

output_size = {'h': None, 'v': None, 'el': None}
for k in output_size:
  if k+'_size' in topoconfig['Output']:
    output_size[k] = float(topoconfig['Output'][k+'_size'])

if output_size['h'] is None and output_size['v'] is None:
  print("At least one of h_size, v_size must be specified", file=sys.stderr)
  exit(2)

if mode=="3d" and output_size['el'] is None:
  print("el_size must be specified for 3d models", file=sys.stderr)
  exit(2)

if mode=="iso" and ("iso" not in topoconfig['Output'] or
    "iso_unit" not in topoconfig['Output']):
  print("iso and iso_unit must be specified for iso drawings", file=sys.stderr)
  exit(2)

output_pts = {'h': None, 'v': None}
for k in output_pts:
  if k+'_pts' in topoconfig['Output']:
    output_pts[k] = int(topoconfig['Output'][k+'_pts'])

if output_pts['h'] is None and output_pts['v'] is None:
  print("At least one of h_pts, v_pts must be specified", file=sys.stderr)
  exit(2)

center = [(box[0][0] + box[2][0])/2, (box[0][1] + box[2][1])/2]

cos_lat = math.cos(math.pi/180 * (box[0][0]+box[2][0])/2)
width = ((box[1][0] - box[0][0])**2 + (cos_lat*(box[1][1] - box[0][1]))**2)**0.5
height = ((box[2][0] - box[1][0])**2 + (cos_lat*(box[2][1] - box[1][1]))**2)**0.5
aspect_ratio = width / height

if output_size['h'] is None:
  output_size['h'] = output_size['v'] * aspect_ratio
if output_size['v'] is None:
  output_size['v'] = output_size['h'] / aspect_ratio
if output_pts['h'] is None:
  output_pts['h'] = int(output_pts['v'] * aspect_ratio)
if output_pts['v'] is None:
  output_pts['v'] = int(output_pts['h'] / aspect_ratio)

# fetch topo data
locations_per_request = 400

def grouper(iterable, n, fillvalue=None):
  "Collect data into fixed-length chunks or blocks"
  # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
  args = [iter(iterable)] * n
  return itertools.zip_longest(*args, fillvalue=fillvalue)

all_locations = []
for i in range(output_pts['v']):
  for j in range(output_pts['h']):
    x = i/(output_pts['v']-1)
    y = j/(output_pts['h']-1)
    la = (1-x)*((1-y)*box[0][0] + y*box[1][0]) + x*((1-y)*box[3][0] +
        y*box[2][0])
    lo = (1-x)*((1-y)*box[0][1] + y*box[1][1]) + x*((1-y)*box[3][1] +
        y*box[2][1])

    all_locations.append((la, lo))

base_url = "https://maps.googleapis.com/maps/api/elevation/json?key="+api_key+"&locations="

elev_data = {}
precision = int(-math.log10(min(map(abs, [box[0][0] - box[2][0], box[1][0] - box[3][0],
  box[0][1] - box[2][1], box[1][1] - box[3][1]]))/
  max(output_pts['h'], output_pts['v'])))+2
format_string = "{:."+str(precision)+"f}"
for locations in grouper(all_locations, locations_per_request):
  url = base_url + urllib.parse.quote("|".join((format_string+","+format_string)
    .format(*location) for location in locations if location is not None))
  print("Submitting request . . . ", end="")
  resp = urllib.request.urlopen(url)
  s = resp.read().decode()
  jo = json.loads(s, parse_float=str)
  print("received", len(jo['results']), "results")
  for r in jo['results']:
    elev_data[(r['location']['lng'], r['location']['lat'])] = r['elevation']
  time.sleep(0.05)

if mode=="3d":
  # output STL file
  el_lim = (min(map(float, elev_data.values())),
      max(map(float, elev_data.values())))
  elev_data_scaled = {}
  for i in range(output_pts['v']):
    for j in range(output_pts['h']):
      (la, lo) = all_locations[i*output_pts['h']+j]
      lt = format_string.format(la).rstrip('0')
      ln = format_string.format(lo).rstrip('0')
      el = output_size['el'] * ((float(elev_data[(ln, lt)]) - el_lim[0])
          / (el_lim[1] - el_lim[0])) - output_size['el']/2
      x = output_size['v']*i/(output_pts['v']-1) - output_size['v']/2
      y = output_size['h']*j/(output_pts['h']-1) - output_size['h']/2
      elev_data_scaled[(i, j)] = (x, y, float(el))

  l_prec = int(-math.log10(min(output_size['h'], output_size['v'])/
    max(output_pts['h'], output_pts['v'])))+2
  el_prec = int(-math.log(output_size['el']))+3
  with open(out_file, "w") as of:
    print("solid Topo", file=of)
    for i in range(output_pts['v']-1):
      for j in range(output_pts['h']-1):
        print("facet normal 0 0 0", file=of)
        print("  outer loop", file=of)
        print("    vertex {0:{1}f} {2:{3}f} {4:{5}f}".format(
          elev_data_scaled[(i, j)][1], l_prec,
          elev_data_scaled[(i, j)][0], l_prec,
          elev_data_scaled[(i, j)][2], el_prec), file=of)
        print("    vertex {0:{1}f} {2:{3}f} {4:{5}f}".format(
          elev_data_scaled[(i+1, j)][1], l_prec,
          elev_data_scaled[(i+1, j)][0], l_prec,
          elev_data_scaled[(i+1, j)][2], el_prec), file=of)
        print("    vertex {0:{1}f} {2:{3}f} {4:{5}f}".format(
          elev_data_scaled[(i, j+1)][1], l_prec,
          elev_data_scaled[(i, j+1)][0], l_prec,
          elev_data_scaled[(i, j+1)][2], el_prec), file=of)
        print("  endloop", file=of)
        print("endfacet", file=of)
        print("facet normal 0 0 0", file=of)
        print("  outer loop", file=of)
        print("    vertex {0:{1}f} {2:{3}f} {4:{5}f}".format(
          elev_data_scaled[(i+1, j)][1], l_prec,
          elev_data_scaled[(i+1, j)][0], l_prec,
          elev_data_scaled[(i+1, j)][2], el_prec), file=of)
        print("    vertex {0:{1}f} {2:{3}f} {4:{5}f}".format(
          elev_data_scaled[(i+1, j+1)][1], l_prec,
          elev_data_scaled[(i+1, j+1)][0], l_prec,
          elev_data_scaled[(i+1, j+1)][2], el_prec), file=of)
        print("    vertex {0:{1}f} {2:{3}f} {4:{5}f}".format(
          elev_data_scaled[(i, j+1)][1], l_prec,
          elev_data_scaled[(i, j+1)][0], l_prec,
          elev_data_scaled[(i, j+1)][2], el_prec), file=of)
        print("  endloop", file=of)
        print("endfacet", file=of)
    print("endsolid Topo", file=of)
elif mode=="iso":
  # TODO: figure this out
  pass
