'''
Created on Mar 18, 2016

@author: Alex
'''
import csv
from utils import hour_day_from_timestamp, base_time
from config import free_states,driver_state_stats_dump_file, log_break_threashold,driver_state_stats_input_file
import grid
from input_data import logs, clear_logs


lat_bins = grid.lat_bins
lng_bins = grid.lng_bins


'''
public variables
'''
drivers = {}
state_stats = {}


# if there is a whole hour between two timestamp, return that timestamp; 
# else return null
def hour_boundary_timestamp_between_two(timestamp1, timestamp2):
    hour_1 = (timestamp1 - base_time)/ 3600
    hour_2 = (timestamp2 - base_time)/ 3600
    return None if hour_1==hour_2 else (hour_1+1) * 3600 + base_time
class Driver:
    def __init__(self, driver_id, initial_log):
        self.id = driver_id
        # this will look like "0101" : [("1-30",0):23,("2-32",1):30]
        self.hour_dict = {}
        # attributes for last_log -> timestamp, state, zone, hour
        self.last_log = initial_log
        # current hour will be updated on rolling basis
        #self.current_hour = ""
        
    def _add_time_to_hour(self, state, hour, time, zone=-1):
        if time==0: return
        if hour not in self.hour_dict:
            self.hour_dict[hour] = {}
        if zone == -1: # not differentiating zones
            if state in self.hour_dict[hour]:
                self.hour_dict[hour][state] += time
            else:
                self.hour_dict[hour][state] = time
        else: # used when we've introduced zones
            # credit half of time to last log's hour if change zone 
            if (zone,state) in self.hour_dict[hour]:
                if (zone,state) != (self.last_log["zone"],self.last_log["state"]) and time>1:
                    self.hour_dict[hour][(zone,state)] += time
                else:
                    self.hour_dict[hour][(zone,state)] += time
            else:
                self.hour_dict[hour][(zone,state)] = time
    def _repalce_last_log(self, new_timestamp, new_state, new_hour, new_zone=-1):
        self.last_log = {"ts": new_timestamp,"state":new_state, "hour": new_hour, "zone":new_zone}
#         if new_zone != -1:
#             self.last_log["zone"] = new_zone
    def new_log(self, new_timestamp, new_state, new_hour, new_zone=-1):
        time = (new_timestamp - self.last_log["ts"]+29)/60
        if time< log_break_threashold:
            if new_hour == self.last_log["hour"]:
                if (new_zone,new_state) != (self.last_log["zone"],self.last_log["state"]) and time>1:
                    self._add_time_to_hour(new_state, new_hour,time / 2, new_zone)
                    self._add_time_to_hour(self.last_log["state"], self.last_log["hour"],
                                           time / 2, self.last_log["zone"])
                else:
                    self._add_time_to_hour(new_state, new_hour, time, new_zone)
            else:
                hour_timestamp = hour_boundary_timestamp_between_two(new_timestamp, self.last_log["ts"])
                if hour_timestamp!= None:
                    time1 = (hour_timestamp - self.last_log["ts"] + 29)/60
                    time2 = (new_timestamp - hour_timestamp +29)/60
                    self._add_time_to_hour(self.last_log["state"], self.last_log["hour"], 
                                           time1, self.last_log["zone"])
                    self._add_time_to_hour(new_state, new_hour, time2, new_zone)
        self._repalce_last_log(new_timestamp, new_state, new_hour, new_zone)
    def __str__(self):
        return self.hour_dict
# end of class Driver    


#############
# Reader
#############
def readlogfile_duration_stay():
    # print time_list
    num_records_free = 0
    num_records_total = 0
    # (did, time, time_bin, lat, lng, lat_ref, lng_ref, state)
    for row in logs:
        num_records_total += 1
        state = row[7] # state
        # discard if the driver is not free
        # if state != "0": continue
        if state in free_states: num_records_free += 1
        lat_ref = row[5]
        lng_ref = row[6]
        zone_slug = "{0},{1}".format(lat_ref,lng_ref)
        time = int(row[1]) # time
        driver_id = row[0] #driver-id
        day, hour = hour_day_from_timestamp(time)
        hour_slug = str(day).zfill(2) + str(hour).zfill(2)
        if driver_id in drivers:
            drivers[driver_id].new_log(time, state, hour_slug, zone_slug)
        else:
            drivers[driver_id] = Driver(driver_id, {"ts":time, "state":state, "zone":zone_slug, "hour":hour_slug})
                
    print "Percentage free {0}".format(float(num_records_free)/(num_records_total+1))
    # transfer drivers to state_stats
    for driver in drivers:
        state_stats[driver] = drivers[driver].hour_dict
###########
# Writer
###########
def dump():
    with open (driver_state_stats_dump_file,"wb") as f:
        header = "driver-id,hour,lat,long,s0,s1,s2,s3,s4,s5,s6,s7,s8,s9,s10\n"
        f.write(header)
        for driver in sorted(state_stats):
            for hour in sorted(state_stats[driver]):
                hour_dict = drivers[driver].hour_dict[hour]
                hour_dict_new = {}
                for (zone,state) in sorted(hour_dict ):
                    if zone not in hour_dict_new: 
                        hour_dict_new[zone] = {state:hour_dict[(zone,state)]}
                    else:
                        hour_dict_new[zone][state] = hour_dict[(zone,state)]
                for zone in hour_dict_new:
                    this_zone = hour_dict_new[zone]
                    line = "{0},{1},{2}".format(driver, hour, zone)
                    for n in range(0,11):
                        if n in this_zone:
                            line+= ","+str(this_zone[n])
                        else:
                            line+= ",0"
                    f.write(line+"\n")
def load():
    global state_stats
    if state_stats:
        print "WARNING: state_stats is already initialised"
        state_stats = {}
    with open(driver_state_stats_input_file) as f:
        reader = csv.DictReader(f, quoting=csv.QUOTE_NONE)
        for row in reader:
            did = int(row["driver-id"])
            if did not in state_stats:
                state_stats[did] = {}
            hour = row["hour"]
            if hour not in state_stats[did]:
                state_stats[did][hour] = {}
            lat_ref = row["lat"]
            lng_ref = row["long"]
            zone_slug = lat_ref+","+lng_ref
            for state_num in range(0,11):
                curr_state = int(row["s"+str(state_num)])
                if curr_state != 0:
                    state_stats[did][hour][(zone_slug,state_num)] = curr_state
def main(**kwargs):
    if not kwargs["reload"] and kwargs["dump"]: return
    print "-------------------------------------"
    print "Processing driver state stats..."
    if kwargs["reload"]:
        print "Reloading state stats..."
        readlogfile_duration_stay()
        logs = None
        clear_logs()
    else:
        print "Loading state stats from disc..."
        # check_input_file()
        load()
    if kwargs["dump"]:
        print "Dumping state stats..."
        dump()