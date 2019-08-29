#!/usr/bin/env python
import math
import sys
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image

#if len(sys.argv) != 2:
#  print("Usage: {} topo.tif".format(sys.argv[0]), file=sys.stderr)
#  exit(1)

#img = np.array(Image.open(sys.argv[1]))
img = np.array(Image.open("./bpc.tif"))
pts = np.nonzero(img > 0)
hts = img[pts[0], pts[1]]
pts = np.transpose(pts)
tri = Delaunay(pts)

v = np.vstack([pts.transpose(), hts])

# output STL file
min_dim = np.expand_dims(np.amin(v, 1), 1)
max_dim = np.expand_dims(np.amax(v, 1), 1)

v = (v - min_dim)/(max_dim - min_dim)

with open('bcp.stl', "w") as of:
  print("solid Topo", file=of)
  for t in tri.simplices:
    print("facet normal 0 0 0", file=of)
    print("  outer loop", file=of)
    for i in range(3):
      print("    vertex {} {} {}".format(
        v[0, t[i]], v[1, t[i]], v[2, t[i]]), file=of)
    print("  endloop", file=of)
    print("endfacet", file=of)
  print("endsolid Topo", file=of)
