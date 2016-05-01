'''
Created on Apr 25, 2016

@author: Alex
'''
import random
import string


time_frame=dict(start_day=9, start_hour=0,
                end_day=10,   end_hour=23,
                year = 2012, month = 4)

file_slug = "{0}{1}{2}{3}{4}{5}".format(time_frame["year"], time_frame["month"], 
                                        time_frame["start_day"], time_frame["start_hour"], 
                                        time_frame["end_day"], time_frame["end_hour"])
file_dir = ""
auto_file_slug = False
if auto_file_slug:
    file_slug = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))


'''
# source files
'''
# log_file = "/home/taxi/2012/04/logs/logs-1204-normal.csv"
# trip_file = "/home/taxi/2012/04/trips/trips-1204-normal.csv"
# trip_ext_file = "/home/taxi/2012/04/trips/trips-1204-normal-ext.csv"

log_file = "F:\\RA\\data\\0907log-head.csv"
trip_file = "F:\\RA\\data\\0907trip-head.csv"
trip_ext_file = "F:\\RA\\data\\0907tripext-head.csv"

'''
# grid grains
'''
map_boundaries=dict(min_lat = 1.20, min_lng = 103.50,
                    max_lat = 1.48, max_lng = 104.14)



sg_border_file = "F:\\RA\\sg-border.kml"
# sg_border_file = "sg-border.kml"


grain_lat_km = 1
grain_lng_km = 1
grid_input_file_json="{0}grid_input_file_{1}.json".format(file_dir,file_slug)
grid_dump_json = grid_input_file_json

'''
# input data
'''
trip_input_file="{0}trips_{1}.csv".format(file_dir,file_slug)
log_input_file="{0}logs_{1}.csv".format(file_dir,file_slug)
trip_dump_file = trip_input_file
log_dump_file = log_input_file

'''
# driver state stats
'''
driver_state_stats_input_file = "{0}driver_state_stats_{1}.csv".format(file_dir,file_slug)
driver_state_stats_dump_file = driver_state_stats_input_file
log_break_threashold = 20 # in minutes
'''
# relative_demand
'''
rd_grid_input_file_json = "{0}rd_grid_{1}.json".format(file_dir,file_slug)
rd_grid_dump_json = rd_grid_input_file_json
rd_grid_dump_csv = rd_grid_dump_json.replace("json", "csv")
free_states = [0]

'''
# driver income
'''
driver_income_input_file = "{0}driver_income_{1}.csv".format(file_dir,file_slug)
driver_income_dump_file = driver_income_input_file

'''
# zone driver
'''
zone_driver_input_file_json= "{0}zone_driver_{1}.json".format(file_dir,file_slug)
output_to_json= False
zone_driver_dump_csv = zone_driver_input_file_json.replace("json", "csv")
zone_driver_dump_json = zone_driver_input_file_json
zone_driver_aggregated = "{0}zone_driver_aggregated_{1}.csv".format(file_dir,file_slug)

def update_time_frame(new_time_frame):
    global time_frame, file_slug,trip_input_file,trip_dump_file,log_input_file,log_dump_file
    global rd_grid_input_file_json,rd_grid_dump_json,rd_grid_dump_csv,driver_state_stats_input_file,driver_state_stats_dump_file
    global driver_income_input_file,driver_income_dump_file,zone_driver_input_file_json
    global zone_driver_dump_csv,zone_driver_dump_json,zone_driver_aggregated
    global grid_input_file_json,grid_dump_json
    time_frame = new_time_frame
    file_slug = "{0}{1}{2}{3}{4}{5}".format(time_frame["year"], time_frame["month"], 
                                        time_frame["start_day"], time_frame["start_hour"], 
                                        time_frame["end_day"], time_frame["end_hour"])
    
    grid_input_file_json="{0}grid_input_file_{1}.json".format(file_dir,file_slug)
    grid_dump_json = grid_input_file_json

    trip_input_file="{0}trips_{1}.csv".format(file_dir,file_slug)
    log_input_file="{0}logs_{1}.csv".format(file_dir,file_slug)
    trip_dump_file = trip_input_file
    log_dump_file = log_input_file
    
    rd_grid_input_file_json = "{0}rd_grid_{1}.json".format(file_dir,file_slug)
    rd_grid_dump_json = rd_grid_input_file_json
    rd_grid_dump_csv = rd_grid_dump_json.replace("json", "csv")
    
    driver_state_stats_input_file = "{0}driver_state_stats_{1}.csv".format(file_dir,file_slug)
    driver_state_stats_dump_file = driver_state_stats_input_file
    
    driver_income_input_file = "{0}driver_income_{1}.csv".format(file_dir,file_slug)
    driver_income_dump_file = driver_income_input_file
    
    zone_driver_input_file_json= "{0}zone_driver_{1}.json".format(file_dir,file_slug)
    zone_driver_dump_csv = zone_driver_input_file_json.replace("json", "csv")
    zone_driver_dump_json = zone_driver_input_file_json
    zone_driver_aggregated = "{0}zone_driver_aggregated_{1}.csv".format(file_dir,file_slug)