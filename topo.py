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

lat_lim = sorted(list(map(float,
  [topoconfig['Point 1']['lat'], topoconfig['Point 2']['lat']])))
lon_lim = sorted(list(map(float,
  [topoconfig['Point 1']['lon'], topoconfig['Point 2']['lon']])))

output_size = {'lat': None, 'lon': None, 'el': None}
for k in output_size:
  if k+'_size' in topoconfig['Output']:
    output_size[k] = float(topoconfig['Output'][k+'_size'])

if output_size['lat'] is None and output_size['lon'] is None:
  print("At least one of lat_size, lon_size must be specified", file=sys.stderr)
  exit(2)

if output_size['el'] is None:
  print("el_size must be specified", file=sys.stderr)
  exit(2)

output_pts = {'lat': None, 'lon': None}
for k in output_pts:
  if k+'_pts' in topoconfig['Output']:
    output_pts[k] = int(topoconfig['Output'][k+'_pts'])

if output_pts['lat'] is None and output_pts['lon'] is None:
  print("At least one of lat_pts, lon_pts must be specified", file=sys.stderr)
  exit(2)

cos_lat = math.cos(math.pi * sum(lat_lim) / 360)
aspect_ratio = (lon_lim[1] - lon_lim[0])*cos_lat / (lat_lim[1] - lat_lim[0])
if output_size['lat'] is None:
  output_size['lat'] = output_size['lon'] / aspect_ratio
if output_size['lon'] is None:
  output_size['lon'] = output_size['lat'] * aspect_ratio
if output_pts['lat'] is None:
  output_pts['lat'] = int(output_pts['lon'] / aspect_ratio)
if output_pts['lon'] is None:
  output_pts['lon'] = int(output_pts['lat'] * aspect_ratio)


# fetch topo data
locations_per_request = 256

def grouper(iterable, n, fillvalue=None):
  "Collect data into fixed-length chunks or blocks"
  # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
  args = [iter(iterable)] * n
  return itertools.zip_longest(*args, fillvalue=fillvalue)

all_locations = itertools.product(
    (lat_lim[0] + (lat_lim[1] - lat_lim[0])*i/output_pts['lat'] for i in
      range(output_pts['lat']+1)),
    (lon_lim[0] + (lon_lim[1] - lon_lim[0])*i/output_pts['lon'] for i in
      range(output_pts['lon']+1)))

base_url = "https://maps.googleapis.com/maps/api/elevation/json?key="+api_key+"&locations="

elev_data = {}
lat_precision = int(-math.log((lat_lim[1] - lat_lim[0])/output_pts['lat'], 10))+2
lon_precision = int(-math.log((lon_lim[1] - lon_lim[0])/output_pts['lon'], 10))+2
format_string = "{:."+str(lat_precision)+"f},{:."+str(lon_precision)+"f}"
for locations in grouper(all_locations, locations_per_request):
  url = base_url + urllib.parse.quote("|".join(format_string.format(*location) for location in locations if location is not None))
  resp = urllib.request.urlopen(url)
  s = resp.read().decode()
  jo = json.loads(s, parse_float=str)
  for r in jo['results']:
    elev_data[(r['location']['lng'], r['location']['lat'])] = r['elevation']
  time.sleep(0.1)

# output STL file
lats = set()
lons = set()
for lt, ln in elev_data:
  lats.add(lt)
  lons.add(ln)
el_lim = (min(map(float, elev_data.values())),
    max(map(float, elev_data.values())))

lats = sorted(lats, key=float)
lons = sorted(lons, key=float)

elev_data_scaled = {}
for i in range(len(lats)):
  for j in range(len(lons)):
    lt = output_size['lat'] * ((float(lats[i]) - lat_lim[0]) /
        (lat_lim[1] - lat_lim[0]))
    ln = output_size['lon'] * ((float(lons[j]) - lon_lim[0]) /
        (lon_lim[1] - lon_lim[0]))
    el = output_size['el'] * ((float(elev_data[(lats[i], lons[j])]) - el_lim[0])
        / (el_lim[1] - el_lim[0]));
    elev_data_scaled[(i, j)] = (lt, ln, el)

print("solid Topo")
for i in range(len(lats)-1):
  for j in range(len(lons)-1):
    print("facet normal 0 0 0")
    print("  outer loop")
    print("    vertex {} {} {}".format(
      elev_data_scaled[(i, j)][1],
      elev_data_scaled[(i, j)][0],
      elev_data_scaled[(i, j)][2]))
    print("    vertex {} {} {}".format(
      elev_data_scaled[(i+1, j)][1],
      elev_data_scaled[(i+1, j)][0],
      elev_data_scaled[(i+1, j)][2]))
    print("    vertex {} {} {}".format(
      elev_data_scaled[(i, j+1)][1],
      elev_data_scaled[(i, j+1)][0],
      elev_data_scaled[(i, j+1)][2]))
    print("  endloop")
    print("endfacet")
    print("facet normal 0 0 0")
    print("  outer loop")
    print("    vertex {} {} {}".format(
      elev_data_scaled[(i+1, j)][1],
      elev_data_scaled[(i+1, j)][0],
      elev_data_scaled[(i+1, j)][2]))
    print("    vertex {} {} {}".format(
      elev_data_scaled[(i+1, j+1)][1],
      elev_data_scaled[(i+1, j+1)][0],
      elev_data_scaled[(i+1, j+1)][2]))
    print("    vertex {} {} {}".format(
      elev_data_scaled[(i, j+1)][1],
      elev_data_scaled[(i, j+1)][0],
      elev_data_scaled[(i, j+1)][2]))
    print("  endloop")
    print("endfacet")
print("endsolid Longs")
