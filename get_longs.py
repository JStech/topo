#!/usr/bin/env python3
import itertools
import json
import sys
import time
import urllib.parse
import urllib.request

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
