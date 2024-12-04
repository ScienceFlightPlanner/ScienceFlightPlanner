import pandas as pd
import numpy as np
import os
import glob

import sys

def decimal_degrees_to_ddm(decimal_degrees):
    '''
    function to convert decimal degrees to decimal minutes
    input: decimal degree
    output: degree, decimal minutes
    '''
    degrees = int(decimal_degrees) # get degrees
    decimal_minutes = (decimal_degrees - degrees) * 60 # convert minutes to decimal minutes
    decimal_minutes = np.round(decimal_minutes, decimals=1) # round to format necessary for gfp format (1 decimal)
    return degrees, decimal_minutes # get degree integer and decimal minutes

def convert2stringLon(val):
    '''
    function to convert Longitude to string with E/W indicator and d/m as deg and minute sign
    '''
    deg = val[0]
    min = val[1]
    if deg<0:
        EastWest = 'W'
        min = abs(min) # remove minus sign
        deg = abs(deg) # remove minus sign
    else:
        EastWest = 'E'
    return('{:1}{:03d}d{:04.1f}m'.format(EastWest,deg,min))

def convert2stringLat(val):
    '''
    function to convert Latitude to string with S/N indicator and d/m as deg and minute sign
    '''
    deg = val[0]
    min = val[1]
    if deg<0:
        NorthSouth = 'S'
        min = abs(min) # remove minus sign
        deg = abs(deg) # remove minus sign
    else:
        NorthSouth = 'N'
    return('{:1}{:02d}d{:04.1f}m'.format(NorthSouth,deg,min))

def dec2ddm(fname):
    '''
    function to read in wpt file as exported by MACS, converts DECDeg to DMM, and saves it back
    output: Same as input with DECDeg will be in DDM
    '''
    dtype_dict = {0: str, 1: str, 2: np.float64,3: np.float64}
    f = pd.read_csv(fname, header=None,dtype = dtype_dict)
    #f = pd.read_csv(fname, header=None)

    lat = list(map(decimal_degrees_to_ddm, f.iloc[:,2]))
    lon = list(map(decimal_degrees_to_ddm, f.iloc[:,3]))

    lon = list(map(convert2stringLon,lon))
    lat = list(map(convert2stringLat,lat))
    f[2] = lat
    f[3] = lon

    f.to_csv(fname[:-4]+'_DDM.wpt',header=False,index = False) # saves file with extension DDM

if __name__ == '__main__':
    fname = sys.argv[1]
    dec2ddm(fname)
