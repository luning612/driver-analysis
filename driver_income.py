'''
Created on Apr 27, 2016

@author: Alex
'''
from config import driver_income_input_file,driver_income_dump_file
from input_data import trips
import csv

driver_income = {}

def load_trip():
    # TRIP TUPLE (did, fare, start_time, time_bin, lat, lng, lat_ref, lng_ref)
    for trip in trips:
        did = trip[0]
        if did not in driver_income:
            driver_income[did] = {}
        time_bin = trip[3]
        if time_bin not in driver_income[did]:
            driver_income[did][time_bin] = 0
        fare = trip[1]
        driver_income[did][time_bin] += fare
def dump():
    with open(driver_income_dump_file, "wb") as f:
        f.write("driver-id,time-bin,income\n")
        for did in sorted(driver_income):
            for time_bin in sorted(driver_income[did]):
                fare = driver_income[did][time_bin]
                f.write("{0},{1},{2}\n".format(did,time_bin,round(fare,5)))
def load():
    with open(driver_income_input_file,"rb") as f:
        reader = csv.DictReader(f, quoting=csv.QUOTE_NONE)
        for row in reader:
            did = row["driver-id"]
            if did not in driver_income:
                driver_income[did] = {}
            time_bin = row["time-bin"]
            fare = float(row["income"])
            driver_income[did][time_bin] = fare
            
def main(**kwargs):
    if not kwargs["reload"] and kwargs["dump"]: return
    print "-------------------------------------"
    print "Starting processing driver income..."
    if kwargs["reload"]:
        print "Processing driver income..."
        load_trip()
    else:
        print "Loading driver income file..."
        load()
    if kwargs["dump"]:
        print "Dumping driver income..."
        dump()