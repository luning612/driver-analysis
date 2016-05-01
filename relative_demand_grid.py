
# This file loads trips files and grids generated by grid-with-stands.py
# which contains json-encoded grid containers and latitude/longitude bins
# It plots trips into the grids, grouped by time
# Author: Alex Lu
#
#
import json
from copy import deepcopy
import grid
from input_data import trips
from driver_state_stats import state_stats
from config import rd_grid_dump_json, rd_grid_input_file_json,rd_grid_dump_csv
from json import encoder
encoder.FLOAT_REPR = lambda o: str(round(o, 5))


# to store the loaded grid
_grid_proto ={}

# bins
lat_bins = []
lng_bins = []


grid_time = {}
new_grid_time = {}

def bin_iterator(grid):
    for lat_ref in grid.keys():
        for lng_ref in grid[lat_ref].keys(): 
            yield grid[lat_ref][lng_ref], lat_ref, lng_ref
def load_grid():
    global lat_bins, lng_bins,_grid_proto
    
    # read grid properties from grid module
    _grid_proto = grid.grid
    lat_bins =   grid.lat_bins
    lng_bins =   grid.lng_bins
    # add in new attributes
    for bin_, lat_ref, lng_ref in bin_iterator(_grid_proto):
        bin_["log-value"] = 0
        bin_["relative-demand"] = 0
        _grid_proto[lat_ref][lng_ref] = bin_
       
def read_trips():
    _out_of_bound = 0
    for row in trips:
        # TRIP TUPLE (did, fare, start_time, time_bin, lat, lng, lat_ref, lng_ref)
        # parse data
        lat_ref = row[6]
        lng_ref = row[7]
        time_bin = row[3]
        if time_bin not in grid_time: 
            grid_time[time_bin] = deepcopy(_grid_proto)
        # add trip record to the grid
        try:
            grid_time[time_bin][lat_ref][lng_ref]["count"] +=1
        except KeyError:
            _out_of_bound+=1
    print "Number of trips out of bound {0}".format(_out_of_bound)
def read_state_stats():
    _out_of_bound = 0
    for driver in state_stats:
        for hour in state_stats[driver]:
            for (zone, state) in state_stats[driver][hour]:
                try:
                    value = state_stats[driver][hour][(zone, state)]
                    if state ==0 and value>0:
                        lat_ref = zone.split(",")[0]
                        lng_ref = zone.split(",")[1]
                        grid_time[hour][lat_ref][lng_ref]["log-value"] += value
                except:
                    _out_of_bound+=1
    print "Number of logs out of bound {0}".format(_out_of_bound)
''' synthesize the new grid based on new input '''
def process_new_grid():
    global new_grid_time
    ###### step 0: create new grid from grid_proto ######
    new_grid = deepcopy(_grid_proto)
    
    ###### step 1: remove zones from never visited for all time ######
    # remove zones never visited for all time
    ''' get cummulated_count for a particular zone '''
    def get_num_pickup(lat_ref, lng_ref):
        pickups = 0
        for time_bin in grid_time.keys():
            if lat_ref in grid_time[time_bin] and lng_ref in grid_time[time_bin][lat_ref]:
                # test if the pickup is positive
                pickups_in_time_bin = grid_time[time_bin][lat_ref][lng_ref]["count"]
                if pickups_in_time_bin > 0:
                    pickups += pickups_in_time_bin
        return pickups
    ''' remove a zone from all time bins '''
    def remove_zone(lat_ref, lng_ref):
            if lat_ref in new_grid.keys() and lng_ref in new_grid[lat_ref]:
                new_grid[lat_ref].pop(lng_ref)
    for lat_ref in _grid_proto.keys():
        for lng_ref in _grid_proto[lat_ref].keys():
            pickups = get_num_pickup(lat_ref, lng_ref)
            if pickups == 0: # no pickups in all time checked
                remove_zone(lat_ref, lng_ref)
        if len(new_grid[lat_ref])==0:
            new_grid.pop(lat_ref)
    ####### step 2: add in time factor. for each time frame, calculate avg (bar) ####
    #######         and determine if each zone is popular                        ####
    # define a container for this task grid_time

    
    def calculate_avg (total, count):
        avg = 0
        try: avg = float(total)/count
        except: pass
        return avg
    for time_bin in grid_time:
        time_bin_pickups = 0 # total number of pickups for this time bin
        time_bin_zone_count = 0 # total number of significant zones
        # initiate grid for this time bin
        new_grid_time[time_bin] = {}
        # add to time_bin_pickups and time_bin_zone_count
        for zone, lat_ref, lng_ref in bin_iterator(grid_time[time_bin]):
            pickups = float(zone["count"])/(zone["log-value"]) if zone["log-value"] else 0
            grid_time[time_bin][lat_ref][lng_ref]["relative-demand"] = pickups
            # log_value = zone["log-value"]
            if pickups > 0: 
                time_bin_pickups += pickups
                time_bin_zone_count += 1
        # calculate avg
        time_bin_avg = calculate_avg(time_bin_pickups,time_bin_zone_count)
        # create new new grids in time series
        _time_bin_zone_count = 1
        _time_bin_zone_above_avg = 0
        for lat_ref in new_grid:
            new_grid_time[time_bin][lat_ref] = {}
            for lng_ref in new_grid[lat_ref]:
                curr_zone_gp = _grid_proto[lat_ref][lng_ref]
                # create sub-container for curr time frame
                curr_ngt = {"demand":grid_time[time_bin][lat_ref][lng_ref]["count"],
                            "supply":grid_time[time_bin][lat_ref][lng_ref]["log-value"],
                            "relative-demand":grid_time[time_bin][lat_ref][lng_ref]["relative-demand"],
                            "is-popular":0}
                _time_bin_zone_count += 1
                for key in ["lat","lng"]: curr_ngt[key] = curr_zone_gp[key]
                if curr_ngt["relative-demand"] > time_bin_avg:
                    _time_bin_zone_above_avg += 1
                    curr_ngt["is-popular"] = 1
                new_grid_time[time_bin][lat_ref][lng_ref] = curr_ngt
        print "time: {0}\t avg:{1}\t total: {2}\t aboveAvg: {3}\t percentage{4}".format(time_bin, time_bin_avg, _time_bin_zone_count, _time_bin_zone_above_avg, float(_time_bin_zone_above_avg)/_time_bin_zone_count)
def write():
    with open(rd_grid_dump_json,"wb") as f:
        f.write(json.dumps(new_grid_time, sort_keys=True)+"\n")
        f.write(json.dumps(lat_bins)+"\n")
        f.write(json.dumps(lat_bins)+"\n")
def write_csv():
    with open(rd_grid_dump_csv, "wb") as f:
        f.write("time,lat-ref,long-ref,lat,long,demand,supply,relative-demand,is-popular\n")
        for time in sorted(new_grid_time):
            for lat_ref in sorted(new_grid_time[time]):
                for lng_ref in sorted(new_grid_time[time][lat_ref]):
                    curr = new_grid_time[time][lat_ref][lng_ref]
                    f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(time,lat_ref,lng_ref,
                                                                           curr["lat"],curr["lng"],
                                                                           curr["demand"],curr["supply"],
                                                                           curr["relative-demand"],
                                                                           curr["is-popular"]))
def load():
    with open(rd_grid_input_file_json,"r") as f:
        new_grid_time = json.loads(f.readline().strip())
        _lat_bins = json.loads(f.readline().strip())
        _lat_bins = json.loads(f.readline().strip())
def main(**kwargs):
    if not kwargs["reload"] and kwargs["dump"]: return
    print "-------------------------------------"
    print "Processing relative demand grid..."
    if kwargs["reload"]:
        print "Reading grid..."
        load_grid()
        # load trip data
        print "Reading trips..."
        read_trips()
        # load state stats
        print "Reading state stats..."
        read_state_stats()
        # process grid
        print "Generating new grid..."
        process_new_grid()
    else:
        print "Loading relative demand grid from disc..."
        load()
    if kwargs["dump"]:
        print "Dumping relative demand grid..."
        write()
    if kwargs["dump_csv"]:
        print "Dumping relative demand grid (csv)..."
        write_csv()
    
            