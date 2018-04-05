#!/usr/bin/env python3
from collections import defaultdict
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
