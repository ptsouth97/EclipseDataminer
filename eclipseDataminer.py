import pandas as pd
import matplotlib.pyplot as plt
from astropy.stats import LombScargle
import astropy.units as u
import numpy as np

# http://ogledb.astrouw.edu.pl/~ogle/photdb/getobj.php?field=BUL_SC48&starid=144757&db=DIA&points=good

def main():
    '''main program for determining period and epoch of a candidate eclipsing variable'''
    name = input('What is the name of the candidate variable? ')
    dat = get_data_from_web()
    plot_data(dat)
    # freq = find_freq(dat)                             # skipping this step for now and...
    freq = 0.1317                                       # giving it a known value for testing purposes
    folded_df = fold_light_curve(freq, dat)
    epoch, zeroed = set_min_to_zero(folded_df)
    phased, ecl_duration = add_phases(zeroed)
    adj = adjust_epoch(phased, ecl_duration)
    phased.loc[:, 'Phase'] = phased.loc[:, 'Phase'].apply(lambda x: x - adj)

    period = round(1 / freq, 4)
    # print('The period is {} days'.format(period))
    epoch = round(epoch + period * adj, 3)
    # print('The epoch is {}'.format(epoch))

    plt.scatter(phased['Phase'], phased['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.title(name + ' (P = ' + str(period) + ' d)')
    plt.grid()
    plt.show()


def get_data_from_web():
    '''Returns a .dat file from OGLE database as a dataframe'''
    url = 'http://ogledb.astrouw.edu.pl/~ogle/photdb/data//bul_sc48_i_144757.dat'   # test url
    df = pd.read_csv(url, delim_whitespace=True)                                    # create data frame
    df.columns = ['HJD', 'mag', 'mag_err', 'photometry_flag', 'frame_grade']        # assign column names from OGLE
    return df


def plot_data(df):
    '''plots the raw data as a test to ensure data was imported properly'''
    df.plot(kind='scatter', x='HJD', y='mag')
    plt.gca().invert_yaxis()
    plt.title('Visual check of raw data')
    plt.show(block=True)


def find_freq(dt):
    '''Uses astropy's LombScargle method to search for frequency with the highest power'''
    t = dt['HJD']
    t_days = t * u.day
    y = dt['mag']
    y_mags = y * u.mag
    #frequency = np.linspace(0.1, 0.2, 10000)
    frequency, power = LombScargle(t_days, y_mags).autopower(minimum_frequency=0.13,
                                                             maximum_frequency=0.132,
                                                             samples_per_peak=1000)
    '''plt.figure(1)
    plt.subplot(211)
    plt.plot(frequency, power)
    plt.xlabel('Frequency')
    plt.ylabel('Lomb-Scargle Power')
    # plt.show()'''
    best_frequency = frequency[np.argmax(power)]
    return best_frequency


def fold_light_curve(fq, dataframe):
    '''Creates a folded light curve (phase 0 - 1) based on frequency found with find_freq'''

    # create a new column in the dataframe to hold the phase values generated from the frequency
    dataframe.loc[:, 'Phase'] = dataframe.loc[:, 'HJD'].apply(lambda x: x*fq%1)

    return dataframe


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

    plt.scatter(update2['Phase'], update2['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.minorticks_on()
    plt.grid(b=True, which='major', color='red', linestyle='-')
    plt.grid(b=True, which='minor', color='green', linestyle='-')
    plt.title('LOOK AT THE PHASE OF THE ECLIPSE')
    plt.show()

    duration = input('What is the duration of the phase of the primary eclipse? ')
    return update2, duration


def adjust_epoch(theDf, dur):
    '''Plots just the primary eclipse data points. Because the minimum magnitude observed does not necessarily
    match the true minimum at phase 0, the data points need to be adjusted by looking at the offset of the shape of
    the eclipse from phase 0. To do this, two nearly equivalent magnitude points are located on opposite sides of
    the parabola and the midway point between them is calculated.  This value represents the needed offset'''
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
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.title('Red line should appear half-way between two yellow points')
    plt.axvline(x=offset, color='red')                          # plot vertical line halfway between chosen data points
    plt.grid()
    plt.show()
    return offset


if __name__ == '__main__':
	main()