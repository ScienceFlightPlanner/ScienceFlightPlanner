import pandas as pd
import numpy as np
import os
import glob
import sys
import re 

def wpNameChanger(fname):
    '''
     fname: filename ; requirement:
           iii_sitecode_user.wpt with iii being a 3 digit ID code. 
           the waypointName will be composed of iiillo (i: ID code,l: linenumber such as 01,o:order such as A/B) 
    route: routeType; values: 
            'grid' for gridded flightmisison, waypoint name requirement: FL_ll_A or FL_ll_B (ll stands for line number 01,02 etc)
            'transect' for a routing flightmission, waypoint name requirement: iii## (iii for ID code, ## for wapoint number, e.g 00101,00102,00103)
    file needs to be a user.wpt file with 4 comma separated columns and no header: 
        waypoint name (up to 6 upper case characters), waypoint comment (up to 25 upper case characters), Lat [DD], Lon[DD], 
    output: Same table with name: iii_sitecode_user_renamed.wpt; renamed WPTname and WPTcomment according to Garmin requirements:
        WPTname: if grid: iiillA / iiillB (e.g. 00112A,00112B for line 12 of target with ID 001 and direction A to B)
                 if transect: iii##, iii##+1 ( e.g 00112,00113 for waypoint 12 and 13 of target with ID 001 )
        WPTcomment: changed to upper Case letters in case there is non-uppercase letters, reduced to first 15 letters + 7 last letters in case longer than 22 letters

    '''

    ID = str(os.path.basename(fname)).split('_')[0]
    # check if ID has only 2 digits
    if len(ID)<3:
        ID = '0'+ ID #make sure id is only 3 digits long and upper case
        ID = ID.upper()
    if len(ID)>3:
        ID = ID[0:3]#make sure id is only 3 digits long and upper case
        ID = ID.upper()

    types_dict = {0: str, 1: str,2:float,3:float}
    f = pd.read_csv(fname,header=None,dtype=types_dict) #import file

    # check routing type: created by macs = grid? or selfmade with only following coordinates?
    # the default export of MACS mission planner is FL_ll_A, with ll beeing the linenumber, let's check if that is the format, then routtype = 'grid'
    print(f.iloc[0,0])
    if (f.iloc[0,0].isnumeric()) and (len(f.iloc[0,0])==5):       
        route = 'transect'
        print('The flightmission type detected is {}'.format(route))
    elif (f.iloc[0,0][0:2] =='FL') and (re.findall("[A-B]", f.iloc[0,0])):
        route = 'grid'
        print('The flightmission type detected is {}'.format(route))
    else:
        raise ValueError('route must be either grid (WPname: FL_ll_A) or transect (WPname: iii##). your WPname is {}'.format(f.iloc[0,0]))

    if route == 'grid':
        #create names
        numbers = [wpName[2:4] for wpName in f.iloc[:,0]] # the default export of MACS mission planner is FL_01_A
        order = [wpName[5] for wpName in f.iloc[:,0]] # the last character of the default export
        WPrenamed = [str(ID)+n+o for n,o in zip(numbers, order)] # combine the info

        f[0] = WPrenamed # overwrite names
    if route == 'transect':
        #create names
        numbers = [wpName[3:5] for wpName in f.iloc[:,0]] # the required name is iii## with iii for ID and ## number of target/coordinate
        WPrenamed = [str(ID)+n for n in numbers] # combine the info, ID gets extracted by the filename

        f[0] = WPrenamed # overwrite names


    siteCode = os.path.basename(fname).split('_')# get the remaining site code of filename
    siteCode = [s.upper() for s in siteCode] # Garmin requires only uppercase letters
    siteCode = ''.join(siteCode[0:-1]) # get all info in filename apart from user.wpt
    if len(siteCode)>22: # garmin only allows for 25 digits in the comment column
        siteCode_old = siteCode
        siteCode = siteCode_old[:14] + siteCode_old[-7:]
        print(f'Caution: Comment has more than 25 characters. We have renamed it for you.\n  OLD:\t{siteCode_old}\n  NEW:\t{siteCode}')
    if route == 'grid':
        comment = [siteCode+n+o for n,o in zip(numbers,order)] #combine comment line
    if route == 'transect':
        comment = [siteCode+n for n in numbers] #combine comment line
    f[1] = comment # overwrite comment name in original file
    f.to_csv(fname[:-4]+'_renamed.wpt',header=False,index = False) # export file

if __name__ == '__main__':
    fname = sys.argv[1]
    wpNameChanger(fname)
