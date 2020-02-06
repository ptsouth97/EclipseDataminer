#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import object_info, aavso, lombscargle, cross_id, phase_adjustments, parameters, initial_setup, plotting
from matplotlib.ticker import FormatStrFormatter
import shutil, os
from pathlib import Path


def main():
	'''main program loop for determining period and epoch of a candidate eclipsing variable \
	and then graphing its corresponding periodiagram and phase plot'''

	print_header()
	print('')

	# read the query file, create a dataframe, define the size and starting point in the df
	# decide how close for a cross-id, and decide whether or not to run fully auto or with user input
	df, total, start, how_close, auto_choice = initial_setup.read_query()

	home = os.getcwd()
		
	# The primary loop that goes through each row of the dataframe df
	for obj in range(start, total):

		print('Now checking object {} of {}...'.format(str(obj), str(total)))

		# slice coordinates from data frame and convert right ascension in hours to decimal degrees
		ra_h = df.iloc[obj][3]
		ra_d = float(ra_h) * 360 / 24 

		dec_d = df.iloc[obj][4]
		
		# check AAVSO's index (VSX) to see if variable star already exists at given position; check_vsx returns '1' if none found
		proceed, vsx_name, vsx_type = aavso.check_vsx(ra_d, dec_d, how_close)

		# append df with vsx star id and vsx star type
		df.ix[obj, 'vsx_id'] = vsx_name
		df.ix[obj, 'vsx_type'] = vsx_type

		# If there is already a nearby variable (nearby defined by 'how_close'), move to the next object
		if proceed != '1':      
			continue

		# set the field name, star id (sid), and url of the object
		field_nm =  str(df.iloc[obj][0])
		sid = str(df.iloc[obj][1])
		print('The field name is ' + field_nm + ' and the star_id is ' + sid)
		name, url = object_info.set_name(field_nm, sid)

		# get the data from the url just generated with the object's name then plot raw data to validate
		dat = object_info.get_data_from_web(url)
		if dat.empty == True:
			continue

		# Select only those data points graded as A, B, or C and exclude D, E, and F
		dat = dat.loc[dat['frame_grade'].isin(['A', 'B', 'C'])]
		# print(select_dat)
       
		# Plot the raw data that was just pulled from the web
		plotting.plot_raw_data(dat, name, auto_choice)
		print('')

		# At this point the user can decide whether or not to proceed based on their visual interpretation of the data
		# In the future, the fully automatic feature will make this decision based on machine learning
		if auto_choice == '1':
			pattern = '1'

		else:
			# Skipping analysis to generate csv file with vsx id and type
			# pattern=input('Continue analysis based on the plot of the raw data?[1]=Yes; [2]=No; [other key]=quit ').strip()
			# print('')
			pattern = '2'

		delete_unused_file = name + '_Raw_Data.png'

		if pattern == '2':
			os.remove(delete_unused_file)
			continue

		if pattern != '1':   
			os.remove(delete_unused_file)
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
	
		print('New name is ' + new_name)

		# search for a frequency that yields an acceptable phase plot
		freq, folded_df = lombscargle.find_freq(dat, name, auto_choice)
		folded_df.to_csv('test_folded_df.csv')

		# make adjustments to phase plot
		epoch, zeroed = phase_adjustments.set_min_to_zero(folded_df)
		phased = phase_adjustments.add_phases(zeroed, auto_choice)

		adj = phase_adjustments.set_epoch(phased, auto_choice)
		phased.loc[:, 'Phase'] = phased.loc[:, 'Phase'].apply(lambda x: x - adj)

		# calculate relevant parameters, place in data frame, and then write to file
		period = parameters.final_csv(freq, epoch, adj, phased, auto_choice, name, final_df)

		print('The name is ' + name)
		# plot finalized phase diagram
		plotting.final_phase_diagram(phased, name, period, auto_choice)

		os.chdir(home)

	# output df to csv file
	df.to_csv('output.csv')

	print('Good bye...')


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
