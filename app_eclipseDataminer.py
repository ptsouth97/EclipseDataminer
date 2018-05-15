#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import object_info, aavso, lombscargle, cross_id, phase_adjustments, parameters, read_query
from matplotlib.ticker import FormatStrFormatter
import shutil, os
from pathlib import Path


def main():
	'''main program loop for determining period and epoch of a candidate eclipsing variable \
	and then graphing its corresponding periodiagram and phase plot'''

	print_header()
	print('')

	while True:
		try:
			txt_file = input('Enter the query text file name: ')   # 'query_2017-10-18_19_39_03.txt'
			df = read_query.load_query(txt_file)
			break

		except ValueError:
			print('Sorry, that file does not exist. Please try again')
			print('')

	total = len(df)
	print('There are {} objects in the query file'.format(str(total)))
	print('')

	start = int(input('Which object do you want to start on? '))
	print('')

	how_close = int(input('What distance in arcmin would you like to use to decide if the object is already classified? '))
	print('')

	auto_choice = input('Do you want to run the analysis [1] fully automated or [any other key] with user input? ').strip()
	home = os.getcwd()
		

	for obj in range(start, total):

		print('Now checking object {} of {}...'.format(str(obj), str(total)))

		# slice coordinates from data frame and convert right ascension in hours to decimal degrees
		ra_h = df.iloc[obj][3]
		ra_d = float(ra_h) * 360 / 24  # convert to decimal degrees

		dec_d = df.iloc[obj][4]
		
		# check AAVSO's VSX to see if variable star already exists at given position before proceeding
		proceed = aavso.check_vsx(ra_d, dec_d, how_close)
		if proceed != '1':      # if there is already a nearby variable, move to the next object
			continue

        # set the field name, star id (sid), and url of the object
		field_nm = str(df.iloc[obj][0])
		sid = str(df.iloc[obj][1])
		print('The field name is ' + field_nm + ' and the star_id is ' + sid)
		name, url = object_info.set_name(field_nm, sid)

		# get the data from the url just generated with the object's name then plot raw data to validate
		dat = object_info.get_data_from_web(url)
		if dat.empty == True:
			continue       
		plot_raw_data(dat, name, auto_choice)
		print('')

		if auto_choice == '1':
			pattern = '1'
		else:
			pattern=input('Do you want to continue analysis based on the plot of the raw data?[1]=Yes; [other key]=No ').strip()

		if pattern != '1':
			continue
		if pattern == '3':
			break

		# create a new folder for the object and generate an empty dataframe to hold the analysis parameters
		final_df, path = object_info.make_folder(name)

		# move the csv and png files into the newly created folder and switch to the new folder
		path_to_file = Path(path + '/RAW_DATA.csv')

		if path_to_file.is_file() == False:
			shutil.move('./RAW_DATA.csv', path)
			shutil.move(name + '_Raw_Data.png', path)
			
		os.chdir(path)

		# check VizieR to cross match with objects in other catalogs...if in OGLE DIA, change to that name
		new_name, x_matches = cross_id.viz(ra_d, dec_d, field_nm)
		x_matches.to_csv('Possible_cross_ids.csv')
		if new_name != 'Found nothing':
			name = new_name

		# search for a frequency that yields an acceptable phase plot
		freq, folded_df = lombscargle.find_freq(dat, name, auto_choice)

        	# make adjustments to phase plot
		epoch, zeroed = phase_adjustments.set_min_to_zero(folded_df)
		phased = phase_adjustments.add_phases(zeroed, auto_choice)

		adj = phase_adjustments.set_epoch(phased, auto_choice)
		phased.loc[:, 'Phase'] = phased.loc[:, 'Phase'].apply(lambda x: x - adj)

		# calculate relevant parameters, place in data frame, and then write to file
		period = round(1 / freq, 4)
		epoch = round(epoch + period * adj, 3)
		minimum = parameters.find_min(phased, auto_choice)
		maximum = parameters.find_max(phased, auto_choice)
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
		if auto_choice != '1':
			plt.show()

		os.chdir(home)

	print('Good bye...')


def plot_raw_data(df, nme, ac):
	'''plots the raw data as a test to ensure data was imported properly'''

	fig, ax = plt.subplots()
	ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))

	plt.scatter(df['HJD'], df['mag'], color='black', s=5)  # 's' is for marker size

	plt.gca().invert_yaxis()
	plt.title(nme + ' Raw Data')
	plot_name = nme + '_Raw_Data.png'
	plt.savefig(plot_name)
	if ac != '1':
		plt.show()


def print_header():

	print('########################################')
	print('#         ECLIPSE DATA MINER           #')
	print('########################################')
	print('')
	print('*****       ******   ******       ******')
	print('     *     *      * *      *     *')
	print('      *   *        *        *   *')
	print('       * *                   * *')
	print('        *                     *')
	return


if __name__ == '__main__':
	main()
