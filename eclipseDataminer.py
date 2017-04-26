import pandas as pd
import matplotlib.pyplot as plt
from astropy.stats import LombScargle
import astropy.units as u
import numpy as np
import requests
from bs4 import BeautifulSoup
import os


def main():
    '''main program loop for determining period and epoch of a candidate eclipsing variable
    and then graphing its corresponding periodiagram and phase plot'''

    print('########################################')
    print('#         ECLIPSE DATA MINER           #')
    print('########################################')
    print('')
    print('*****       ******   *****       ******')
    print('     *     *      * *     *     *')
    print('      *   *        *       *   *')
    print('       * *                  * *')
    print('        *                    *')

    while True:
        exit = input("Enter [1] to load an object's data or any other key to exit ").strip()
        print('')
        if exit != '1':
            break

        proceed, ra_d, dec_d = check_vsx()
        if proceed != '1':
            break

        name, url, final_df = get_info()
        dat = get_data_from_web(url)
        plot_raw_data(dat, name)
        freq, folded_df = find_freq(dat, name)
        epoch, zeroed = set_min_to_zero(folded_df)
        phased = add_phases(zeroed)
        adj = adjust_epoch(phased)
        phased.loc[:, 'Phase'] = phased.loc[:, 'Phase'].apply(lambda x: x - adj)

        period = round(1 / freq, 4)
        epoch = round(epoch + period * adj, 3)
        final_df.iloc[0][0] = name
        final_df.iloc[0][1] = period
        final_df.iloc[0][2] = epoch
        final_df.to_csv(name + '_Parameters.csv')

        plt.scatter(phased['Phase'], phased['mag'], color='black', s=5)    # 's' is for marker size
        plt.gca().invert_yaxis()
        plt.ylabel('Ic-mag')
        plt.xlabel('Phase')
        plt.title(name + ' (P = ' + str(period) + ' d)')
        plt.grid()
        plt_name = name + '_Phase_Diagram'
        plt.savefig(plt_name)
        plt.show()
        
    print('Good bye...')


def check_vsx() -> object:
    '''Checks coordinates in VSX to see if there is already an identified object at that location'''

    while True:
        ra = input("What is the object's RA in decimal hours? ").strip()         # test value:  ra = '17.473532'
        if float(ra) <= 24 and float(ra) >= 0:
            break
        else:
            print('Please enter a valid RA between 0 and 24 decimal hours')

    while True:
        DEC = input("What is the object's DEC in decimal degrees? ").strip()  # test value:  DEC = '-40.22071'
        if float(DEC) <= 90 and float(DEC) >= -90:
            break
        else:
            print('Please enter a valid DEC between -90 and 90 decimal degrees')

    RA = float(ra) * 360 / 24  # convert to decimal degrees
    coords = str(RA) + '+' + DEC

    url = 'http://www.aavso.org/vsx/index.php?view=results.get&format=d&order=9&coords=' + coords
    print('Checking coordinates in VSX...')
    print('')
    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'lxml')
    table = soup.find_all('table')[10]                                  # grab the table with the relevant object info

    all_tr = table.find_all('tr')                                       # type = ResultSet
    first_entry = all_tr[2]                                             # type = Tag
    results = first_entry.get_text().lstrip(' ')                        # type = string
    dist = results[3:7]
    id = results[11:37].strip()

    if results[3:8] == 'There':
        print('No nearby objects were found')
    else:
        print('The VSX object {} is located {} arcmin from the coordinates you entered'.format(id, dist))
    print('')
    answer = input('Do you wish to proceed? [1]=Yes, [any other key]=No ').strip()
    print('')
    return answer, RA, DEC


def get_info():
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

def check_VizieR():
    '''checks SIMBAD database for cross-IDs'''
    pass


def get_data_from_web(the_name):
    '''Returns a .dat file from OGLE database as a dataframe'''
    base = 'http://ogledb.astrouw.edu.pl/~ogle/photdb/data//'
    url = base + the_name
    df = pd.read_csv(url, delim_whitespace=True)                                    # create data frame
    df.columns = ['HJD', 'mag', 'mag_err', 'photometry_flag', 'frame_grade']        # assign column names from OGLE
    df.to_csv(the_name + '_RAW_DATA.csv')
    return df


def plot_raw_data(df, nme):
    '''plots the raw data as a test to ensure data was imported properly'''

    df.plot(kind='scatter', x='HJD', y='mag')
    plt.gca().invert_yaxis()
    plt.title(nme + ' Raw Data')
    plot_name = nme + ' Raw Data.png'
    plt.savefig(plot_name)
    plt.show()


def find_freq(dt, n):
    '''Uses astropy's LombScargle method to search for frequency with the highest power and then visually check
    if it produces a viable phase plot.  For more see http://docs.astropy.org/en/stable/stats/lombscargle.html'''

    t = dt['HJD']
    t_days = t * u.day
    y = dt['mag']
    y_mags = y * u.mag

    while True:
        print('########################################')
        print('#           PERIOD ANALYSIS            #')
        print('########################################')
        print('')
        print('Lomb Scargle arguments set to default')
        print('')
        method = 'auto'
        numterms = 1
        nyq = 5
        spp = 5
        mod = 0

        while True:
            choice = input('Would you like to modify arguments for Lomb Scargle? 1=Yes, any other key=No ')

            if choice.strip() == '1':
                print('')
                print('What do you want to do?')
                print('1 = Specify method')
                print('2 = Specify nterms')
                print('3 = Specify min & max frequency,')
                print('4 = Specify Nyquist factor')
                print('5 = Specify the frequency')
                print('')
                choice2 = input('What is your choice? ')

                # method
                if choice2.strip() == '1':
                    method = input("What method do you want to use? ('auto', 'fast', 'slow', 'cython', 'chi2', "
                                   "fastchi2', or 'scipy') ").strip().lower()

                # nterms
                if choice2.strip() == '2':
                    if method == 'chi2' or method == 'fastchi2':
                        numterms = int(input('How many Fourier terms do you want to use in the model? ').strip())
                    else:
                        print("Number of terms 'nterms' can only be modified for methods 'chi2' or 'fastchi2'")

                # min/max frequency
                if choice2.strip() == '3':
                    min_freq = float(input('What is the minimum frequency? ').strip())
                    max_freq = float(input('What is the maximum frequency? ').strip())
                    spp = float(input('How many samples per peak? ').strip())
                    mod = 1

                # Nyquist
                if choice2.strip() == '4':
                    nyq = int(input('What Nyquist factor do you want to try? '))
                    mod = 2
                    break

                # specific frequency
                if choice2.strip() == '5':
                    best_frequency = float(input('What frequency do you want to try? '))
                    mod = 3
                    break

            else:
                # frequency, power = LombScargle(t_days, y_mags, nterms=2).autopower(method='chi2')
                # power_sorted = power.argsort()
                # best_frequency = frequency[power_sorted[-2]]
                # best_frequency = frequency[np.argmax(power)]  # most likely frequency is where the power is highest
                break

        if mod == 0:
            frequency, power = LombScargle(t_days, y_mags, nterms=numterms).autopower(method=method)

        if mod == 1:
            frequency, power = LombScargle(t_days, y_mags, nterms=numterms).autopower(method=method,
                                                                                 minimum_frequency=min_freq,
                                                                                 maximum_frequency = max_freq,
                                                                                 samples_per_peak = spp)

        if mod == 2:
            frequency, power = LombScargle(t_days, y_mags).autopower(nyquist_factor=nyq)

        if mod == 3:
            frequency, power = LombScargle(t_days, y_mags).power(best_frequency)

        # power_sorted = power.argsort()
        # best_frequency = frequency[power_sorted[-1]]
        best_frequency = frequency[np.argmax(power)]  # the most likely frequency is where the power is highest
        plt.figure(1)
        plt.subplot(211)
        plt.plot(frequency, power, color='black')
        plt.axvline(x=best_frequency, color='blue', linestyle='dashed')  # plot vertical line at best frequency
        plt.xlabel('Frequency')
        plt.ylabel('Lomb-Scargle Power')
        plt.title('Frequency = ' + str(best_frequency))
        figname = n + 'Periodiagram'
        plt.savefig(figname)

        # create a new column in the dataframe to hold the phase values generated from the frequency
        dt.loc[:, 'Phase'] = dt.loc[:, 'HJD'].apply(lambda x: x*best_frequency%1)

        plt.subplot(212)
        plt.scatter(dt['Phase'], dt['mag'], color='black', s=5)  # 's' is for marker size
        plt.gca().invert_yaxis()
        plt.ylabel('Ic-mag')
        plt.xlabel('Phase')
        plt.show()
        print('')
        satisf = int(input('Is the phase plot satisfactory? 1=Yes or 2=No '))
        print('')
        if satisf == 1:
            break
    return best_frequency, dt


def set_min_to_zero(folded):
    '''Finds the primary eclipse (i.e., largest magnitude) and sets that as phase 0 and adjusts other phase values
    accordingly'''
    zero = folded.sort_values('mag', ascending=False)   # sort the magnitudes from biggest to smallest
    min_phase = zero.iloc[0][5]                         # grab the phase of the largest mag (minima)
    epc = zero.iloc[0][0]                               # grab the Julian Date of the largest mag (minima)

    # Make the minimum magnitude phase 0 by subtracting min_phase; adjust all other phase values accordingly
    zero.loc[:, 'Phase'] = zero.loc[:, 'Phase'].apply(lambda x: x - min_phase if x - min_phase >= 0 else x - min_phase + 1)
    '''plt.scatter(zero['Phase'], zero['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.show()'''
    return epc, zero


def add_phases(zd):
    '''In order to show full eclipse eclipse behavior, adds phases -0.25 to 0 and 1 to 1.25 (full range now
    -0.25 to 1.25 instead of just 0 to 1). To do this, must copy and paste relevant parts of the curve'''

    pd.options.mode.chained_assignment = None  # default='warn', turned off

    # make new df by selecting data points for phase 0.75 to 1 and make them -0.25 to 0 by subtracting 1
    select_last_quartile = zd.loc[zd.loc[:, 'Phase'] >= 0.75]
    select_last_quartile.loc[:, 'Phase'] = select_last_quartile.loc[:, 'Phase'].apply(lambda x: x - 1)

    # make new df by selecting data points for phase 0 to 0.25 and make them 1 to 1.25 by adding 1
    select_first_quartile = zd.loc[zd.loc[:, 'Phase'] <= 0.25]
    select_first_quartile.loc[:, 'Phase'] = select_first_quartile.loc[:, 'Phase'].apply(lambda x: x + 1)

    # append the new -0.25 to 0 and 1 to 1.25 dataframes to the original 0 to 1 phase data
    update1 = zd.append(select_last_quartile, ignore_index=True)
    update2 = update1.append(select_first_quartile, ignore_index=True)

    plt.scatter(update2['Phase'], update2['mag'], s=10)
    plt.gca().invert_yaxis()
    plt.ylabel('Ic-mag')
    plt.xlabel('Phase')
    plt.minorticks_on()
    plt.grid(b=True, which='major', color='red', linestyle='-')
    plt.grid(b=True, which='minor', color='green', linestyle='-')
    plt.title('ESTIMATE THE DURATION OF THE PRIMARY ECLIPSE')
    plt.show()

    return update2


def adjust_epoch(theDf):
    '''Plots just the primary eclipse data points. Because the minimum magnitude observed does not necessarily
    match the true minimum at phase 0, the data points need to be adjusted by looking at the offset of the shape of
    the eclipse from phase 0. To do this, two nearly equivalent magnitude points are located on opposite sides of
    the parabola and the midway point between them is calculated.  This value represents the needed offset'''

    while True:
        while True:
            dur = input('What is the duration of the phase of the primary eclipse? ')
            if float(dur) > 0 and float(dur) < 1:
                break
            else:
                print('Please enter a valid duration that is greater than 0 and less than 1')
        print('')
        theDf = theDf.sort_values('Phase')
        primary_eclipse_1 = theDf.loc[theDf.loc[:, 'Phase'] < float(dur)/2]
        primary_eclipse = primary_eclipse_1.loc[primary_eclipse_1.loc[:, 'Phase'] > -float(dur)/2]
        primary_eclipse.reset_index(drop=True, inplace=True)    # re-order the index starting at 0
        min_dp = primary_eclipse.mag.idxmax()   # min_dp is the index of the minima of the eclipse, i.e., max value
        offset = 0                              # initialize variable for the offset that will be returned
        flag = 0                                # flag variable will signal when to break out of loop once match is found
        mk_1 = 0                                # mk_1 will hold the row location for the first match of the pair
        mk_2 = 0                                # mk_2 will hold the row location for the second match of the pair
        for i in range(0, min_dp + 1):          # check data points from index 0 up to the index of the minima (left side)
            if flag == 1:  break
            for j in range(0, len(primary_eclipse.index) - min_dp): # for each point on left, check every right side point
                if flag == 1: break
                mag_diff = abs(primary_eclipse.iloc[i][1] - primary_eclipse.iloc[-j-1][1])
                if mag_diff < 0.02:     # if the difference in mag is this small, you've found matching points on both sides
                    offset = primary_eclipse.iloc[i][5] + \
                             ((primary_eclipse.iloc[len(primary_eclipse.index) - j - 1][5] - primary_eclipse.iloc[i][5])/2)
                    mk_1 = i
                    mk_2 = len(primary_eclipse.index) - j - 1
                    flag = 1

        if offset == 0:
            print('No match found')

        plt.scatter(primary_eclipse['Phase'], primary_eclipse['mag'])
        plt.scatter(primary_eclipse.iloc[mk_1][5], primary_eclipse.iloc[mk_1][1], color='yellow')
        plt.scatter(primary_eclipse.iloc[mk_2][5], primary_eclipse.iloc[mk_2][1], color='yellow')
        plt.gca().invert_yaxis()
        plt.ylabel('Ic-mag')
        plt.xlabel('Phase')
        plt.title('Red line should appear half-way between two yellow points')
        plt.axvline(x=offset, color='red')                          # plot vertical line halfway between chosen data points
        plt.grid()
        plt.show()
        satisfactory = int(input('Is the location of the vertical offset line satisfactory? 1=Yes or 2=No '))
        print('')
        if satisfactory == 1:
            break
    return offset


if __name__ == '__main__':
	main()