'''
Created on Apr 26, 2016

@author: Alex
'''

def bin_function(day, hour, **kwargs):
    return str(int(day)).zfill(2) + str(int(hour)).zfill(2)

    