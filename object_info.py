import os
import pandas as pd


def main():
    get_info()

def set_name():
    '''store basic information about the object of interest'''
    while True:
        field_name = input('What is the FIELD NAME of the candidate variable? ').strip()
        field_num = input('What is the FIELD NUMBER of the candidate variable? ').strip()
        star_id = input('What is the STAR ID of the candidate variable ').strip()
        print('')
        url_id = field_name.lower() + '_' + field_num.lower() + '_i_' + star_id.lower() + '.dat'
        path_id = 'OGLEII_' + field_name.upper() + '-' + field_num.upper() + '_' + star_id

        print('You entered: ' + path_id + ' and the url_id is ' + url_id)
        print('')
        correct = input('Is this correct?  [1]=Yes, [any other key]=No ').strip()
        if correct == '1':
            break

    newpath = r'C:\Users\Blake\Transporter\Personal Documents' \
              r'\Hobbies and Interests\a. Astronomy\1. AAVSO\Data Mining\Suspects\New stars\\' + path_id
    if not os.path.exists(newpath):
        os.makedirs(newpath)                                                # set up new directory with name of object

    os.chdir(newpath)

    # create new data frame that will hold the information discovered
    columns = ['name', 'period', 'epoch']
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