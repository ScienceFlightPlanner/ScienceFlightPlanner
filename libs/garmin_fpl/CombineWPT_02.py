import pandas as pd
import numpy as np
import glob
import os
import sys

def combineWPT(directory):
    '''
    combines all iii_sitename_user_renamed.wpt files within a directory to one final user.wpt.
    This list is the import file for the Garmin for importing user.wpt. This information containes the names for specific coordinates (here in decimal degree format)
    The iii_sitename_fpl.gfp file only containes the sequence of the different coordinates and extracts their names from this final user.wpt file
    The user.wpt file will be stored in the same folder as all iii_sitename_user.wpt
    input: path to directory of all relevant iii_sitename_user_renamed.wpt of the day
    output: user.wpt
    '''
    wpts = glob.glob(os.path.join(directory,'*_renamed.wpt'))

    def get_df():
        # list of files
        df=pd.DataFrame()
        dtype_dict = {0: str, 1: str, 2: np.float64,3: np.float64}
        for file in wpts:
                f=pd.read_csv(file, header=None,dtype = dtype_dict)
                df=pd.concat([df,f])
        return df

    df = get_df()
    df.to_csv(os.path.join(directory,'user.wpt'), header=False,index = False)

if __name__ == '__main__':
    folder = sys.argv[1]
    combineWPT(folder)
