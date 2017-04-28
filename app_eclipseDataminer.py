import pandas as pd
import matplotlib.pyplot as plt
import object_info, catalogs, lombscargle, cross_id


def main():
    '''main program loop for determining period and epoch of a candidate eclipsing variable
    and then graphing its corresponding periodiagram and phase plot'''

    print_header()
    print('')

    while True:
        exit = input("Enter [1] to load an object's data or any other key to exit ").strip()
        print('')
        if exit != '1':
            break

        proceed, ra_d, dec_d = catalogs.check_vsx()
        if proceed != '1':
            break

        name, url, final_df, field_nm = object_info.set_name()
        dat = object_info.get_data_from_web(url)
        plot_raw_data(dat, name)

        new_name, x_matches = cross_id.viz(ra_d, dec_d, field_nm)
        x_matches.to_csv('Possible_cross_ids.csv')
        if new_name != 'Found nothing':
            name = new_name

        freq, folded_df = lombscargle.find_freq(dat, name)
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


def plot_raw_data(df, nme):
    '''plots the raw data as a test to ensure data was imported properly'''

    df.plot(kind='scatter', x='HJD', y='mag')
    plt.gca().invert_yaxis()
    plt.title(nme + ' Raw Data')
    plot_name = nme + ' Raw Data.png'
    plt.savefig(plot_name)
    plt.show()


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
        satisfactory = input('Is the location of the vertical offset line satisfactory? [1]=Yes or [any other '
                             'key]=No ').strip()
        print('')
        if satisfactory == '1':
            break
    return offset

def print_header():
    print('########################################')
    print('#         ECLIPSE DATA MINER           #')
    print('########################################')
    print('')
    print('*****       ******   *****       ******')
    print('     *     *      * *     *     *')
    print('      *   *        *       *   *')
    print('       * *                  * *')
    print('        *                    *')
    return


if __name__ == '__main__':
	main()