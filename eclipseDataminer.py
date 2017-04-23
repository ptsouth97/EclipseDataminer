import pandas as pd
import matplotlib.pyplot as plt
from astropy.stats import LombScargle
import astropy.units as u
import numpy as np

# http://ogledb.astrouw.edu.pl/~ogle/photdb/getobj.php?field=BUL_SC48&starid=144757&db=DIA&points=good

def main():
    '''main program'''
    name = input('What is the name of the candidate variable? ')
    dat = get_data_from_web()
    dat.columns = ['HJD', 'mag', 'mag_err', 'photometry_flag', 'frame_grade']
    # plot_data(dat)
    #freq = find_freq(dat)
    #print('the frequency is {}'.format(freq))      # skipping this step for now
    freq=0.1317                                     # giving it a known value for testing purposes
    folded_df = fold_light_curve(freq, dat)
    epoch, zeroed = set_min_to_zero(folded_df)
    phased, ecl_duration = add_phases(zeroed)
    adj = adjust_epoch(phased, ecl_duration)
    phased['Phase'] = phased['Phase'].apply(lambda x: x - adj)

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
    url = 'http://ogledb.astrouw.edu.pl/~ogle/photdb/data//bul_sc48_i_144757.dat'
    df = pd.read_csv(url, delim_whitespace=True)
    return df


def plot_data(df):
    '''plots the raw data as a test to ensure data was imported properly'''
    df.plot(kind='scatter', x='HJD', y='mag')
    plt.gca().invert_yaxis()
    plt.show()


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
    dataframe['Phase'] = dataframe['HJD'].apply(lambda x: x*fq%1)
    '''plt.subplot(212)
    plt.scatter(dataframe['Phase'], dataframe['mag'])
    #dataframe.plot(kind='scatter', x='JD', y='mag')
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.show()'''
    return dataframe


def set_min_to_zero(folded):
    '''Finds the primary eclipse (i.e., largest magnitude) and sets that as phase 0 and adjusts other phase values
    accordingly'''
    zero = folded.sort_values('mag',ascending=False) # find the minimum (primary eclipse)
    min_phase = zero.iloc[0][5]
    epc = zero.iloc[0][0]
    zero['Phase'] = zero['Phase'].apply(lambda x: x - min_phase if x - min_phase >= 0 else x - min_phase + 1)
    '''plt.scatter(zero['Phase'], zero['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.show()'''
    return epc, zero


def add_phases(zd):
    '''In order to show full eclipse, adds phases -0.25 to 0 and 1 to 1.25 (full range now -0.25 to 1.25 instead
    of  0 to 1)'''
    select_last_quartile = zd.loc[zd['Phase'] >= 0.75]
    select_last_quartile['Phase'] = select_last_quartile['Phase'].apply(lambda x: x - 1)
    select_first_quartile = zd.loc[zd['Phase'] <= 0.25]
    select_first_quartile['Phase'] = select_first_quartile['Phase'].apply(lambda x: x + 1)
    update1 = zd.append(select_last_quartile, ignore_index=True)
    update2 = update1.append(select_first_quartile, ignore_index=True)
    plt.scatter(update2['Phase'], update2['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='g', linestyle='-')
    plt.grid(b=True, which='minor', color='r', linestyle='-')
    plt.title('LOOK AT THE PHASE OF THE ECLIPSE')
    plt.show()
    duration = input('What is the duration of the phase of the primary eclipse? ')
    return update2, duration


def adjust_epoch(theDf, dur):
    '''Plots just the primary eclipse data points. Because the minimum magnitude observed does not necessarily
    match the true minimum at phase 0, the data points are adjusted by looking at the offset of the shape of
    the eclipse from phase 0'''
    theDf = theDf.sort_values('Phase')
    primary_eclipse_1 = theDf.loc[theDf['Phase'] < float(dur)/2]
    primary_eclipse = primary_eclipse_1.loc[primary_eclipse_1['Phase'] > -float(dur)/2]
    if abs(primary_eclipse.iloc[0][1] - primary_eclipse.iloc[-1][1]) < 0.02:
        print('found match')
        offset = primary_eclipse.iloc[0][5] + (primary_eclipse.iloc[-1][5] - primary_eclipse.iloc[0][5]) / 2
        print(offset)
    plt.scatter(primary_eclipse['Phase'], primary_eclipse['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('mag')
    plt.xlabel('Phase')
    plt.grid()
    plt.show()
    return offset


if __name__ == '__main__':
	main()