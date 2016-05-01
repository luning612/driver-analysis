import bisect
import time
import datetime
from config import time_frame

base_time = None
time_frame_start = None
time_frame_end = None
# search for the bin where the coord belongs
def get_coord_bin(lat, lng, lat_bins, lng_bins):
    #print lat_bins, lng_bins, lat, lng
    i = bisect.bisect_right(lat_bins, lat)
    j = bisect.bisect_right(lng_bins, lng)
    if i and j:
        return str(i-1), str(j-1)
    raise ValueError

def get_base_time ():
    return int( time.mktime(datetime.datetime(time_frame["year"], time_frame["month"], 1, 0).timetuple()))
def get_time_frame_start(): 
    return int(time.mktime(datetime.datetime(time_frame["year"], time_frame["month"],
                                             time_frame["start_day"], time_frame["start_hour"])
                           .timetuple()))
def get_time_frame_end ():
    return int(time.mktime(datetime.datetime(time_frame["year"], time_frame["month"],
                                             time_frame["end_day"], time_frame["end_hour"])
                           .timetuple()))
def hour_day_from_timestamp(timestamp):
    global base_time
    if base_time is None:
        print "base_time is None"
        base_time = get_base_time()
    hour_count = (timestamp - base_time)/ 3600
    hour = hour_count % 24
    day = hour_count /24 +1
    return day, hour
def main():
    global base_time, time_frame_start, time_frame_end
    base_time= get_base_time()
    time_frame_start = get_time_frame_start()
    time_frame_end = get_time_frame_end()