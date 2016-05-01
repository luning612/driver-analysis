'''
Created on Apr 26, 2016

@author: Alex
'''
import itertools
from utils import  get_time_frame_start, get_time_frame_end, get_coord_bin, hour_day_from_timestamp
from config import time_frame,log_file, trip_ext_file, trip_file, free_states, trip_dump_file, log_dump_file, trip_input_file, log_input_file
import grid
from time_bin import bin_function
from itertools import izip_longest



'''
public variables
'''
trips = [] 
logs = []

'''
dependency
'''
lat_bins = []
lng_bins = []

frame_start_time = get_time_frame_start()
frame_end_time = get_time_frame_end()

start_day = time_frame["start_day"]
start_hour = time_frame["start_hour"]
end_day = time_frame["end_day"]
end_hour = time_frame["end_hour"]

def load_grid_bins():
    global lat_bins, lng_bins
    if not grid.lat_bins or not grid.lng_bins:
        raise Exception("lat_bins not initiated")
    lat_bins = grid.lat_bins 
    lng_bins = grid.lng_bins
def process_trip():
    _num_records = 0
    _num_records_invalid = 0
    
    tfile   = open(trip_file, "rb")
    extfile = open(trip_ext_file, "rb")
    #read trip and trip ext file in parallel
    tfile.readline()
    extfile.readline()
    for row1_raw,row2_raw in itertools.izip(tfile,extfile):
        
        row1 = row1_raw.split(",")
        row2 = row2_raw.split(",")
        start_time = int(row1[2])
        if start_time < frame_start_time: continue
        if start_time >= frame_end_time: break
        
        fare  = int(row1[10])
        did   = int(row2[4])
        lat = float(row1[5])
        lng = float(row1[4])
        try:
            lat_ref, lng_ref = get_coord_bin(lat, lng, lat_bins, lng_bins)
        
            # minute = "30" if int(row1["start-minute"]) >=30 else "00"
            time_bin = bin_function(row1[13], row1[14])
            # int, int, int, str, float, float, str, str
            trip = (did, fare, start_time, time_bin, lat, lng, lat_ref, lng_ref)
            trips.append(trip)
            _num_records +=1
        except ValueError:
            _num_records_invalid += 1
    print "Number records {0}\t invalid records {1}".format(_num_records,_num_records_invalid)
def dump_trip():
    with open(trip_dump_file,"wb") as f:
        f.write("did,fare,start_time,time_bin,lat,lng,lat_ref,lng_ref\n")
        for record in trips:
            line = ""
            for attr in record:
                line+= str(attr)+","
            f.write(line[:-1]+"\n")
def load_trip():
    with open(trip_input_file,"r") as f:
        f.readline()
        for row in f:
            # int, int, int, str, float, float, str, str
            row_list = row.strip().split(",")
            for i in [0,1,2]:
                row_list[i] = int(row_list[i])
            for i in [4,5]:
                row_list[i] = float(row_list[i])
            trips.append(tuple(row_list))
def load_log():
    with open(log_input_file,"r") as f:
        f.readline()
        for row in f:
            row_list = row.strip().split(",")
            # int,int,str,float,float,str,str,int
            for i in [0,1,7]:
                row_list[i] = int(row_list[i])
            for i in [3,4]:
                row_list[i] = float(row_list[i])
            logs.append(tuple(row_list))
def dump_log():
    with open(log_dump_file,"wb") as f:
        f.write("did,time,time_bin,lat,lng,lat_ref,lng_ref,state\n")
        for record in logs:
            line = ""
            for attr in record:
                line+= str(attr)+","
            f.write(line[:-1]+"\n")
def process_log():
    _num_records = 0
    _num_records_invalid = 0
    # time, vid, did, long, lat, speed, state
    with open(log_file) as f:
        num_records_free = 0
        f.readline()
        for row_raw in f:
            
            row_one = row_raw.split(",",1)
            # slice data stream
            time = int(row_one[0])
            if time < frame_start_time: continue
            if time >= frame_end_time: break
            
            row = row_raw.split(",")
            state = int(row[6]) # state
            if state in free_states: num_records_free += 1
            lat = float(row[4]) # latitude
            lng = float(row[3]) # longitude
            did = int (row[2]) #driver-id
            # deal with grid bins
            lat_ref, lng_ref = get_coord_bin(lat, lng, lat_bins, lng_bins)
            # deal with time
            try:
                day, hour = hour_day_from_timestamp(time)
                time_bin = bin_function(day, hour)
                # int,int,str,float,float,str,str,int
                log = (did, time, time_bin, lat, lng, lat_ref, lng_ref, state)
                logs.append(log)
                _num_records +=1
                if _num_records % 1000000 ==0:
                    print "...{0} millions lines processed...".format(_num_records/100000)
            except ValueError:
                _num_records_invalid += 1
        print "Number records {0}\t invalid records {1}".format(_num_records,_num_records_invalid)

def process_log_enhanced():
    num_track = dict(records = 0,records_invalid = 0)
    
    def process_row(row):
        # slice data stream
        time = int(row[0])
        if time < frame_start_time: return -1
        if time >= frame_end_time: return 1
        
        state = int(row[6]) # state
        lat = float(row[4]) # latitude
        lng = float(row[3]) # longitude
        did = int (row[2]) #driver-id
        # deal with grid bins
        lat_ref, lng_ref = get_coord_bin(lat, lng, lat_bins, lng_bins)
        # deal with time
        try:
            day, hour = hour_day_from_timestamp(time)
            time_bin = bin_function(day, hour)
            log = (did, time, time_bin, lat, lng, lat_ref, lng_ref, state)
            logs.append(log)
            num_track["records"] +=1
            if num_track["records"] % 1000000 ==0:
                print "...{0} millions lines processed...".format(num_track["records"]/100000)
        except ValueError:
            num_track["records_invalid"] += 1
        return 0
    with open(log_file) as f:
        f.readline()
        
        found_beginning = False
        try:
            for next_n_lines in izip_longest(*[f] * 100):
                if len(next_n_lines)>=1 and next_n_lines[-1] is not None:
                    last_record_time_str = next_n_lines[-1].split(",",1)[0]
                    last_record_time = int(last_record_time_str)
                    if not found_beginning and last_record_time > frame_start_time:
                        found_beginning  = True
                    if found_beginning:
                        for row_raw in next_n_lines:
                            row = row_raw.split(",")
                            action = process_row(row)
                            if action ==1: raise ValueError # to break the loop
                        
        except ValueError, e: 
            print "done", str(e)
        print "Number records {0}\t invalid records {1}".format(num_track["records"],num_track["records_invalid"])

def clear_logs():
    # make sure the logs is referenced from nowhere else
    global logs
    logs = []
def main(**kwargs):
    print "-------------------------------------"
    print "Starting input data extraction..."
    if kwargs["reload_trip"] or kwargs["reload_log"]:
        print "Loading grid bins..."
        load_grid_bins()
    if kwargs["reload_trip"]:
        print "Loading trips..."
        process_trip()
    else:
        print "Reading trips..."
        load_trip() 
    if kwargs["reload_log"]:
        print "Loading logs..."
        process_log_enhanced()
    else:
        print "Reading logs..."
        load_log() 
    if kwargs["dump_trip"]:
        print "Dumping trips..."
        dump_trip()
    if kwargs["dump_log"]:
        print "Dumping logs..."
        dump_log()
    