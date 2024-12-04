import pandas as pd
import os
import sys
import glob
import numpy as np

'''
Script adds a bounding box with ~2 miles around target area. This information can be useful for the pilot for flight planning
input:iii_sitename_user_renamed.wpt
output:iii_sitename_user_renamed_BBox.wpt
'''

def decimal_degrees_to_ddm(decimal_degrees):
    '''
     function to calculate decimal degrees to decimal minutes
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
    return('{:1}{:02d}°{:04.1f}\''.format(EastWest,deg,min))

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
    return('{:1}{:02d}°{:04.1f}\''.format(NorthSouth,deg,min))

def BBoxCeator(fname):
    f = pd.read_csv(fname)

    corners = [min(f.iloc[:,2]), max(f.iloc[:,2]), min(f.iloc[:,3]), max(f.iloc[:,3])]
                # minLat, maxLat, minLon, maxLon

    '''
    Latitude: each minute is approx 1 mile: [+2,-2] for minutes of maxLat and minLat
    Longitute at Lat 68: apporximately 3 minutes correspond to 2 km --> [+3,-3] for minutes of maxLon, minLon
    '''
    cornersDDM = list(map(decimal_degrees_to_ddm, corners))
    bbox_enhancers = [-2,2,-3,+3]

    for i in range(0, len(bbox_enhancers)):
        deg = cornersDDM[i][0]
        minu = cornersDDM[i][1]+bbox_enhancers[i]
        if abs(minu) > 60:
            print(minu)
            print(int(np.round(minu/60,decimals=0)))
            deg = deg + int(np.round(minu/60,decimals=0))
            print(deg)
            minu = np.round(abs(minu) % 60,decimals=1)
            print(minu)
        cornersDDM[i] = (deg,minu)

    # combine to ll,ul,lr,ur

    ll = cornersDDM[0],cornersDDM[2] #Latmin + Lonmin
    ul = cornersDDM[1],cornersDDM[2] #Latmax + Lonmin
    lr = cornersDDM[0],cornersDDM[3] #
    ur = cornersDDM[1],cornersDDM[3]

    bbox = pd.DataFrame(data = [ll,ul,lr,ur])
    
    lats = list(map(convert2stringLat,bbox.iloc[:,0]))
    lons = list(map(convert2stringLon,bbox.iloc[:,1]))
    bbox = pd.DataFrame(data={'lat':lats,'lon':lons})
    bbox.to_csv(fname[:-4]+'_BBox.txt',header=False,index = False)


if __name__ == '__main__':
    fnames = glob.glob(f'{sys.argv[1]}\*_renamed.wpt')
    print(f'{sys.argv[1]}')
    print(fnames)
    list(map(BBoxCeator,fnames))
#print(ll,ul,lr,ur)
#reconvert>


