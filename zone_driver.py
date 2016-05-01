'''
Created on Feb 21, 2016
This module helps study the correlation between proportion in pop zone and driver's income
This module runs through the given log file and creates a timemap for each driver 
and add in num occurrence for pop zone and general.
It then read shift file and trip file (trip extension) for additional information,
such as duration and income
@author: Alex
'''
import json
from config import zone_driver_input_file_json, zone_driver_dump_json, zone_driver_aggregated, output_to_json, zone_driver_dump_csv
from driver_state_stats import state_stats
from relative_demand_grid import new_grid_time
from driver_income import driver_income
from json import encoder
encoder.FLOAT_REPR = lambda o: str(round(o, 5))


# this dict holds all drivers count of popular zones
drivers = {}

def process_zone_driver():
    _num_key_errors = 0
    _num_driver_time= 0
    for did in state_stats:
        if did not in drivers:
            drivers[did]= {}
        for time in state_stats[did]:
            regions = []
            pop_regions = []
            curr_dict = {"num-regions":0, "num-pop-regions":0, "duration-pop-regions": 0,
                         "duration":0, "income":0, "total-region-weight":0,
                         "region-ratio":0, "duration-ratio":0,"income-ratio":0,"region-weight-ratio":0}
            for (region, state) in state_stats[did][time]:
                duration = state_stats[did][time][(region, state)]
                curr_dict["duration"] += duration
                # to count distinct occurrences
                if region not in regions:
                    regions.append(region)
                lat_ref = region.split(",")[0]
                lng_ref = region.split(",")[1]
                # get is-popular and relative demand information from grid
                is_pop_region=0
                region_rd = 0.0
                try:
                    is_pop_region = new_grid_time[time][lat_ref][lng_ref]["is-popular"]
                    region_rd = new_grid_time[time][lat_ref][lng_ref]["relative-demand"]
                except:pass
                curr_dict["total-region-weight"] += region_rd * duration
                if is_pop_region:
                    curr_dict["duration-pop-regions"] += duration
                    # to count distinct occurrences pop regions
                    if region not in pop_regions:
                        pop_regions.append(region)
            # take the income from driver income dict
            try:
                _num_driver_time +=1
                curr_dict["income"] = driver_income[did][time]
            except KeyError:
#                 print did
#                 print time
#                 di_did = driver_income[did]
#                 print "........"
#                 print driver_income
#                 break
                
                _num_key_errors+=1
            # count num of distinct regions and pop regions
            curr_dict["num-regions"] = len(regions)
            curr_dict["num-pop-regions"] = len(pop_regions)
            # calculate ratios
            if curr_dict["num-regions"] != 0:
                # region ratio
                curr_dict["region-ratio"] = curr_dict["num-pop-regions"]/ curr_dict["num-regions"]
            if  curr_dict["duration"] != 0:
                # duration ratio
                curr_dict["duration-ratio"] = curr_dict["duration-pop-regions"]/curr_dict["duration"]
                # income ratio
                curr_dict["income-ratio"] = curr_dict["income"]/curr_dict["duration"]
                # region weight ratio
                curr_dict["region-weight-ratio"] = curr_dict["total-region-weight"]/curr_dict["duration"]
            
            drivers[did][time]= curr_dict
    print "Num driver time {0}\tNum of driver time without trips {1}".format(_num_driver_time,_num_key_errors)
            

def write():
    if output_to_json:
        with open(zone_driver_dump_json, 'wb') as f:
            f.write(json.dumps(drivers, sort_keys=True))
    else:
        with open(zone_driver_dump_csv, 'wb') as f:
            f.write("driver-id,time,num-regions,num-pop-regions,duration,"+
                    "duration-pop-regions,income,total-region-weight,region-ratio,"+
                    "duration-ratio,income-ratio,region-weight-ratio\n")
            for driver in sorted(drivers):
                for time in sorted(drivers[driver]):
                    ci = drivers[driver][time]
                    f.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n"
                            .format(driver,time,ci["num-regions"],ci["num-pop-regions"],
                                    ci["duration"],ci["duration-pop-regions"],ci["income"],
                                    ci["total-region-weight"],round(ci["region-ratio"],5),
                                    round(ci["duration-ratio"],5), round(ci["income-ratio"],5),
                                    round(ci["region-weight-ratio"],5)
                                    )
                            )
def dump_aggregated():
    with open(zone_driver_aggregated,"wb") as out:
        out.write("driver-id,num-regions,num-pop-regions,duration,"+
                "duration-pop-regions,income,total-region-weight,region-ratio,"+
                "duration-ratio,income-ratio,region-weight-ratio\n")
#         "num-regions":0, "num-pop-regions":0, "duration-pop-regions": 0,
#                          "duration":0, "income":0, "total-region-weight":0,
#                          "region-ratio":0, "duration-ratio":0,"income-ratio":0,"region-weight-ratio":0
        for driver_id in sorted(drivers):
            agg_reg = 0
            agg_pop = 0
            agg_dur = 0
            agg_inc = 0
            agg_pdur = 0
            agg_total_region_weight = 0
            for time_bin in drivers[driver_id]:
                cur_bin = drivers[driver_id][time_bin]
                # for region ratio
                agg_reg += cur_bin["num-regions"]
                agg_pop += cur_bin["num-pop-regions"]
                # for duration ratio
                agg_pdur += cur_bin["duration-pop-regions"]
                agg_dur += cur_bin["duration"]
                # for income ratio
                agg_inc += cur_bin["income"]
                # for region-weight-ratio
                agg_total_region_weight += cur_bin["total-region-weight"]
                
            region_ratio = round(float(agg_pop)/agg_reg,4) if agg_reg!=0 else "NaN"
            income_ratio = round(agg_inc/agg_dur, 4) if agg_dur!=0 else "NaN"
            duration_ratio = round(agg_pdur/agg_dur, 4) if agg_dur!=0 else "NaN"
            region_weight_ratio = round(agg_total_region_weight/agg_dur, 4) if agg_dur!=0 else "NaN"
            out.write("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n"
                      .format(driver_id,agg_reg,agg_pop,agg_dur,agg_pdur,agg_inc,
                              agg_total_region_weight,region_ratio,duration_ratio, 
                              income_ratio,region_weight_ratio
                              )
                      )
def load():
    with open(zone_driver_input_file_json,"rb") as f:
        drivers = json.loads(f.readline().strip())
def main(**kwargs):
    if not kwargs["reload"] and kwargs["dump"]: return
    print "-------------------------------------"
    print "Processing zone driver..."
    if kwargs["reload"]:
        print "Generating zone driver..."
        process_zone_driver()
    else:
        print "Reloading zone driver..."
        load()
    if kwargs["dump"]:
        print "Dumping zone driver..."
        write()
    dump_aggregated()