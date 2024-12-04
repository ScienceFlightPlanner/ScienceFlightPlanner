import sys
import os
from pathlib import Path

# read in final user.wpt and create Track.txt file in the format needed for aircraft data acquisition 
in_dir = sys.argv[1] # the user.wpt of the day

#output_dir = sys.argv[2] # filename for the Track.txt

def track_from_userwpt(in_dir, altitude=2800):
    user_wpt = Path(in_dir) / 'user.wpt'
    #in_dir_name = in_dir.name
    track_file = Path(in_dir) / 'Track.txt' #in_dir + f'/{in_dir}_Track.txt',
    with open(user_wpt, 'r') as f:
        # Read lines from the input file
        # input user.wpt has 4 columns: POINTID, COMMENT, LAT, LON
        lines = f.readlines()

    with open(track_file, 'w') as f:
        for line in lines:
            parts = line.strip().split(',')
            # the comment contains the altitude
            comment = parts.pop(1)
            #altitude = int(comment[-8:-4])
            altitude = altitude
            print(parts[0], parts[1], parts[2])
            # we don't need the comment for the Track.txt
            # but the remaining three columns are written with tab-delimiter
            f.write(parts[0] + '\t' + parts[2] + '\t' + parts[1] + '\t' + str(altitude)+'.0' + '\n')   
    
if __name__ == '__main__':
    folder = sys.argv[1]
    if len(sys.argv) == 3:
        altitude = sys.argv[2]
        track_from_userwpt(folder, altitude=altitude)
    else:
        track_from_userwpt(folder)