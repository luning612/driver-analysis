******************
*    Overview    *
****************** 
The purpose of this project is to study the coorelation between individual driver's 
income and the region selection. The input data is trip (trip-text) and log data, and 
the output would be each driver's region ratio, duration ratio, income ratio and 
region weight ratio. The program produces these ratios with and without respect to time 
respectively. These ratios can then be used for linear regression analysis.

The program configurably dumps intermediate results for each module and the user may 
choose to load the result from the previous module and continue from that.

******************
* Configurations *
******************
The configurable variables are in ./config.py.
 
Time_frame includes year, month, start_day (day of month), start_hour (hour of day),
end_day and end_day. A time frame accross months is not supported. Please make sure the 
the year, month value here match the input log and trip file paths.

You may specify the dump data file names and load data file name for each module, if you 
wish to dump/load on hard drive. A file_slug consisting of time frame input is attached to
the output files to differentiate output for different time frames.

If both csv and json dump functions are present, the load function loads the json file only.

By default, free state only consider state_0 (roaming), but you can add additional states.

You may replace the binning function in time_bins.py.

*****************
*     Run       *
*****************
navigate to pwd = driver-analysis/../
python driver-analysis [--sd <start_day>] [--sh <start_hour>] [--ed <end_day>] 
[--eh <end_hour>]

* The command line arguments are OPTIONAL

************************
* Architecture Diagram *
************************

                 .-----------------.      + boundaries (an enclosing rectangle) 
                 |     grid.py     | <--- + sg_border_file.kml
                 |                 |      + grain size
                 '-----------------'
                          |grid 
                          v
                 .-----------------.
                 |  input_data.py  |<---- + log.csv
              .--|                 |---.  + trip.csv + trip-ext.csv
              |  '-----------------'   |
           log|                        |trip
              v                        v
     .----------------.        .---------------.
     |  driver_state  |        | driver_income |
     |   _stats.py    |        |      .py      |
     '----------------'        '---------------'
              |                        |
      state_stats                     driver_income
              |  .-----------------.   |
              '->| relative_demand |<--'
                 |    _grid.py     |
                 '-----------------'
                          |rd_grid         = zone-driver.csv =               
                          v                - Ratios for each driver time_bin:    
                 .-----------------.         region-ratio,duration-ratio,    
                 | zone_driver.py  |----->   income-ratio,region-weight-ratio
                 |                 |       = zone-driver-aggregated.csv =
                 '-----------------'       - Ratios for each driver ( aggregates 
                                             on time_bin dimension
*************************
* Understanding Outputs *
*************************
zone_driver.csv contains region ratio, duration ratio, income ratio and 
region weight ratio. Among these, region ratio, duration ratio and region weight
are used to reflect the general attractiveness of the regions that the driver
selects.

Definitions:
income - the total fare of trips starting in the time bin
total duration - the total log time that the driver is active in the time bin
demand - number of trips starting in the time bin
supply - accumulative time (in minutes) for free state across 
         all drivers that appeared the region
expected demand per minute (aka relative demand) - = supply / supply (if supply==0, rd=0)
significant zone - zones with expected demand per minute greater than average. 
                   It varies with time bin.
significant duration - duration that the driver appears in significant zones

income ratio = income / total duration
duration ratio = significant duration / total duration
region ratio = num of distinct significant regions / num of all regions
total region weight = accumulated (region relative demand * duration in the region)
region weight ratio = total region weight / total duration

