import os
import pandas as pd
from sys import platform

def main():
    set_name()

def set_name(field, star_id):
    '''store basic information about the object of interest'''
    
    url_id = field.lower() + '_i_' + star_id + '.dat'
    path_id = 'OGLEII_' + field + '_' + star_id

    print('You entered: ' + path_id + ' and the url_id is ' + url_id)
    print('')
    '''correct = input('Is this correct?  [1]=Yes, [any other key]=No ').strip()
       if correct == '1':
       break'''

    if platform == 'linux':
        newpath = os.getcwd() + '/' + path_id
    else:
        newpath = os.getcwd() + '\\' + path_id
 
    if not os.path.exists(newpath):
        os.makedirs(newpath)                    # set up new directory with name of object

    os.chdir(newpath)

    # create new data frame that will hold the information discovered
    columns = ['name', 'period', 'epoch', 'minimum', 'maximum']
    new_df = pd.DataFrame(columns=columns, index=range(0, 1))

    return path_id, url_id, new_df


def get_data_from_web(the_name):
    '''Returns a .dat file from OGLE database as a dataframe'''
    base = 'http://ogledb.astrouw.edu.pl/~ogle/photdb/data//'
    url = base + the_name
    df = pd.read_csv(url, delim_whitespace=True)                                    # create data frame
    df.columns = ['HJD', 'mag', 'mag_err', 'photometry_flag', 'frame_grade']        # assign column names from OGLE
    df.to_csv(the_name + '_RAW_DATA.csv')
    return df


if __name__ == '__main__':
	main()
