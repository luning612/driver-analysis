'''
Created on Apr 26, 2016

@author: Alex
'''
import json
from json import encoder
encoder.FLOAT_REPR = lambda o: str(round(o, 5))

from config import grain_lat_km, grain_lng_km,map_boundaries, grid_input_file_json
from config import grid_dump_json, sg_border_file
grain_lat = grain_lat_km * 0.02
grain_lng = grain_lng_km * 0.02

'''
public variables
'''
lat_bins = []
lng_bins = []
grid = {}

_poly = []

def get_sg_border_def():
    global _poly
    with open(sg_border_file) as f:
        kml = f.readline().strip()
        coords = kml.split(',')
        for coord in coords:
            coord = coord.strip().split(' ')
            lng = float(coord[0])
            lat = float(coord[1])
            _poly.append((lat,lng))

# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs. This function
# returns True or False.  The algorithm is called
# the "Ray Casting Method".
def point_in_poly(x,y):
    global _poly
    n = len(_poly)
    inside = False
    p1x,p1y = _poly[0]
    for i in range(n+1):
        p2x,p2y = _poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

def build_grid():
    min_lat = map_boundaries["min_lat"]
    max_lat = map_boundaries["max_lat"]
    min_lng = map_boundaries["min_lng"]
    max_lng = map_boundaries["max_lng"]
    
    #initiate polygon
    get_sg_border_def()
    #get raw grid
    while min_lat < max_lat:
        lat_bins.append(min_lat)
        min_lat = round(min_lat+ grain_lat, 5)
    while min_lng < max_lng:
        lng_bins.append(min_lng)
        min_lng = round(min_lng + grain_lng, 5)
    
    #initialize empty grid
    lat_id  = 0
    lat_ref = 0
    for lat in lat_bins:
        lng_id  = 0
        lng_ref = 0
        curr_lat_bins = {}
        for lng in lng_bins:
            if point_in_poly(lat,lng):
                lng_id += 1
                curr_lat_bins[lng_ref] = {
                    "lat-id":lat_id,
                    "lng-id":lng_id,
                    "lat":round(lat+grain_lat/2, 5),
                    "lng":round(lng+grain_lng/2, 5),
                    "count":0
                }
            lng_ref += 1
        if len(curr_lat_bins)!=0:
            lat_id += 1
            grid[lat_ref] = curr_lat_bins
        lat_ref += 1
def dump():
    with open(grid_dump_json, 'wb') as f:
        f.write(json.dumps(grid, sort_keys=True)+"\n")
        f.write(json.dumps(lat_bins)+"\n")
        f.write(json.dumps(lng_bins)+"\n")   
def load():
    global grid, lat_bins, lng_bins
    with open(grid_input_file_json,"r") as f:
        grid = json.loads(f.readline().strip())
        lat_bins = json.loads(f.readline().strip())
        lng_bins = json.loads(f.readline().strip())

def main(**kwargs):
    if not kwargs["reload"] and kwargs["dump"]: return
    print "-------------------------------------"
    print "start processing grids..."
    if kwargs["reload"]:
        print "building grids..."
        build_grid()
    else: 
        print "loading grids..."
        load()
    if kwargs["dump"]:
        print "dumping grids..."
        dump()
        