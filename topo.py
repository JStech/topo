#!/usr/bin/env python3
from collections import defaultdict
import argparse
import itertools
import json
import sys
import time
import urllib.parse
import urllib.request

# usage
# topo.py lat1 lon1 lat2 lon2 pts1 pts2
parser = argparse.ArgumentParser(description=
    "Download topographical data for a region")
parser.add_argument("lat1", type=float, nargs=1)
parser.add_argument("lon1", type=float, nargs=1)
parser.add_argument("lat2", type=float, nargs=1)
parser.add_argument("lon2", type=float, nargs=1)
parser.add_argument("points1", type=int, nargs=1)
parser.add_argument("points2", type=int, nargs="?")
args = parser.parse_args()
print(args)
exit()

co_lat = (40.227819, 40.289363)
co_lon = (-105.647206, -105.538757)
v_res = 21
h_res = 28

locations_per_request = 256

def grouper(iterable, n, fillvalue=None):
  "Collect data into fixed-length chunks or blocks"
  # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
  args = [iter(iterable)] * n
  return itertools.zip_longest(*args, fillvalue=fillvalue)

all_locations = itertools.product(
    (co_lat[0] + (co_lat[1] - co_lat[0])*i/v_res for i in range(v_res+1)),
    (co_lon[0] + (co_lon[1] - co_lon[0])*i/h_res for i in range(h_res+1)))

with open("gmaps_api_key.txt") as api_key_file:
  api_key = api_key_file.readline().strip()
base_url = "https://maps.googleapis.com/maps/api/elevation/json?key="+api_key+"&locations="

with open("elev_data.txt", "w") as out_file:
  for locations in grouper(all_locations, locations_per_request):
    url = base_url + urllib.parse.quote("|".join("{:.4f},{:.4f}".format(*location) for location in locations if location is not None))
    resp = urllib.request.urlopen(url)
    s = resp.read().decode()
    jo = json.loads(s)
    for r in jo['results']:
      print(r['location']['lng'], r['location']['lat'], r['elevation'], file=out_file)
    time.sleep(0.1)



#!/usr/bin/env python3
deg_lat = 68.99
deg_lon = 53.06

elev = defaultdict(dict)

for line in open('elev_data.txt'):
  (ln, lt, el) = line.split()
  elev[ln][lt] = el

lns = sorted(elev.keys(), reverse=True)
lts = sorted(elev[lns[0]].keys())

print("solid Longs")
for i in range(len(lns)-1):
  for j in range(len(lts)-1):
    print("facet normal 0 0 0")
    print("  outer loop")
    print("    vertex {} {} {}".format(deg_lon*float(lns[i]),
      deg_lat*float(lts[j]), 1e-3*float(elev[lns[i]][lts[j]])))
    print("    vertex {} {} {}".format(deg_lon*float(lns[i+1]),
      deg_lat*float(lts[j]), 1e-3*float(elev[lns[i+1]][lts[j]])))
    print("    vertex {} {} {}".format(deg_lon*float(lns[i]),
      deg_lat*float(lts[j+1]), 1e-3*float(elev[lns[i]][lts[j+1]])))
    print("  endloop")
    print("endfacet")
    print("facet normal 0 0 0")
    print("  outer loop")
    print("    vertex {} {} {}".format(deg_lon*float(lns[i+1]),
      deg_lat*float(lts[j]), 1e-3*float(elev[lns[i+1]][lts[j]])))
    print("    vertex {} {} {}".format(deg_lon*float(lns[i+1]),
      deg_lat*float(lts[j+1]), 1e-3*float(elev[lns[i+1]][lts[j+1]])))
    print("    vertex {} {} {}".format(deg_lon*float(lns[i]),
      deg_lat*float(lts[j+1]), 1e-3*float(elev[lns[i]][lts[j+1]])))
    print("  endloop")
    print("endfacet")
print("endsolid Longs")
