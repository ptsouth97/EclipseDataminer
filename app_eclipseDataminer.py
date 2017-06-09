
import pandas as pd
import matplotlib.pyplot as plt
import object_info, catalogs, lombscargle, cross_id, phase_adjustments, parameters
from matplotlib.ticker import FormatStrFormatter


def main():
    '''main program loop for determining period and epoch of a candidate eclipsing variable
    and then graphing its corresponding periodiagram and phase plot'''

    print_header()
    print('')

    while True:
        # load data or quit application
        exit = input("Enter [1] to load an object's data or any other key to exit ").strip()
        print('')
        if exit != '1':
            break

        # check AAVSO's VSX to see if variable star already exists at given position before proceeding
        proceed, ra_d, dec_d = catalogs.check_vsx()
        if proceed != '1':
            break

        # set the name of the variable, make a new folder & url with that name, and set empty data frame for results
        name, url, final_df, field_nm = object_info.set_name()

        # get the data from the url just generated with the object's name then plot raw data to validate
        dat = object_info.get_data_from_web(url)
        plot_raw_data(dat, name)

        # check VizieR to cross match with objects in other catalogs...if in OGLE DIA, change to that name
        new_name, x_matches = cross_id.viz(ra_d, dec_d, field_nm)
        x_matches.to_csv('Possible_cross_ids.csv')
        if new_name != 'Found nothing':
            name = new_name

        # search for a frequency that yields an acceptable phase plot
        freq, folded_df = lombscargle.find_freq(dat, name)

        # make adjustments to phase plot
        epoch, zeroed = phase_adjustments.set_min_to_zero(folded_df)
        phased = phase_adjustments.add_phases(zeroed)

        adj = phase_adjustments.set_epoch(phased)
        phased.loc[:, 'Phase'] = phased.loc[:, 'Phase'].apply(lambda x: x - adj)

        # calculate relevant parameters, place in data frame, and then write to file
        period = round(1 / freq, 4)
        epoch = round(epoch + period * adj, 3)
        minimum = parameters.find_min(phased)
        maximum = parameters.find_max(phased)
        final_df.iloc[0][0] = name
        final_df.iloc[0][1] = period
        final_df.iloc[0][2] = epoch
        final_df.iloc[0][3] = minimum
        final_df.iloc[0][4] = maximum
        final_df.to_csv(name + '_Parameters.csv')

        # plot finalized phase diagram
        fig, ax = plt.subplots()
        ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
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

    fig, ax = plt.subplots()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))

    plt.scatter(df['HJD'], df['mag'], color='black', s=5)  # 's' is for marker size

    plt.gca().invert_yaxis()
    plt.title(nme + ' Raw Data')
    plot_name = nme + ' Raw Data.png'
    plt.savefig(plot_name)
    plt.show()


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
