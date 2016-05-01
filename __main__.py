'''
Created on Apr 26, 2016

@author: Alex
'''
# import cProfile
import sys, getopt
def main(argv):
    load_all = True
    dump_all = True
    curr_frame = dict(start_day=1, start_hour=0,end_day=1,end_hour=1,year = 2009, month = 7)
    from config import update_time_frame
    try:
        opts, args = getopt.getopt(argv,"h",["sd=","sh=","ed=","eh="])
    except getopt.GetoptError:
        print 'driver-analysis --sd --sh --ed --eh '
        sys.exit(2)
    for opt, arg in opts:
        if opt == 'h':
            print 'driver-analysis --sd --sh --ed --eh '
            sys.exit()
        elif opt=="--sd":
            curr_frame["start_day"] = int(arg)
        elif opt=="--sh":
            curr_frame["start_hour"] = int(arg)
        elif opt=="--ed":
            curr_frame["end_day"] = int(arg)
        elif opt=="--eh":
            curr_frame["end_hour"] = int(arg)
    print curr_frame
#     time_frame_list = [dict(start_day=1, start_hour=0,end_day=1,end_hour=1,year = 2009, month = 7),
#                        dict(start_day=10, start_hour=0,end_day=11,end_hour=0,year = 2012, month = 4),
#                        dict(start_day=11, start_hour=0,end_day=12,end_hour=0,year = 2012, month = 4),
#                        dict(start_day=12, start_hour=0,end_day=13,end_hour=0,year = 2012, month = 4),
#                        dict(start_day=13, start_hour=0,end_day=14,end_hour=0,year = 2012, month = 4),
#                        dict(start_day=15, start_hour=0,end_day=16,end_hour=0,year = 2012, month = 4),
#                        ]
    update_time_frame(curr_frame)
    import utils
    utils.main()
    
    import grid
    grid.main(reload=load_all, dump=dump_all)
    
    import input_data
    # cProfile.run('input_data.main(reload_trip=load_all, reload_log=load_all, dump_trip=dump_all, dump_log=dump_all)')
    input_data.main(reload_trip=load_all, reload_log=load_all, dump_trip=dump_all, dump_log=dump_all)
     
    import driver_income
    driver_income.main(reload=load_all, dump=dump_all)
     
    import driver_state_stats
    driver_state_stats.main(reload=load_all, dump=dump_all)
     
    import relative_demand_grid
    relative_demand_grid.main(reload=load_all, dump= dump_all, dump_csv = dump_all)
     
    import zone_driver
    zone_driver.main(reload=load_all, dump= dump_all)
    print "job done!"
if __name__ == "__main__":
    main(sys.argv[1:])
