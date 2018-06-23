#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
import os


def main():
	'''main function for testing:  reads an example folded light curve dataframe '''

	os.chdir('./test_folder')

	print('Testing mode')
	print('')

	test_df = pd.read_csv('test_folded_df.csv')

	set_min_to_zero(test_df)	


def set_min_to_zero(folded):
	'''Finds the primary eclipse (i.e., largest magnitude) and sets that as phase 0 and adjusts other phase values
	accordingly'''
	
	# sort the magnitudes from biggest to smallest
	zero = folded.sort_values('mag', ascending=False)
	
	# grab the phase of the largest mag (minima)
	min_phase = zero.iloc[0][5] 
	
	# grab the Julian Date of the largest mag (minima)
	epc = zero.iloc[0][0]                               

	# Make the minimum magnitude phase 0 by subtracting min_phase; adjust all other phase values accordingly
	zero.loc[:, 'Phase'] = zero.loc[:, 'Phase'].apply(lambda x: x - min_phase if x - min_phase >= 0 else x - min_phase + 1)
	
	# Plot here, if testing
	if __name__ == '__main__':

		# Before shift	
		plt.figure(1)
		plt.subplot(211)
		plt.title('Before shifting to minimum mag at phase 0')
		plt.scatter(folded['Phase'], folded['mag'])
		plt.gca().invert_yaxis()
		plt.ylabel('mag')
		plt.xlabel('Phase')

		# After shift
		plt.subplot(212)
		plt.title('After shifting to minimum mag at phase 0')
		plt.scatter(zero['Phase'], zero['mag'])
		plt.gca().invert_yaxis()
		plt.ylabel('mag')
		plt.xlabel('Phase')
		plt.tight_layout()
		plt.show()
		
	return epc, zero


def add_phases(zd, atc):
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
	
	if atc != '1':
		plt.show()

	return update2


def set_epoch(theDf, autoc):
	'''Plots just the primary eclipse data points. Because the minimum magnitude observed does not necessarily
	match the true minimum at phase 0, the data points need to be adjusted by looking at the offset of the shape of
	the eclipse from phase 0. To do this, two nearly equivalent magnitude points are located on opposite sides of
	the parabola and the midway point between them is calculated.  This value represents the needed offset'''

	# See if it's possible to use an if-statement to bypass the duration question, i.e., ask for EA, EB, or EW
	while True:

		# Get the duration of the eclipse (n/a for EB and EW types)
		while True:
			if autoc == '1':
				dur = float(0.2)
				break
			else:
				dur = input('What is the duration of the phase of the primary eclipse? ')
				if float(dur) > 0 and float(dur) < 1:
					break
				else:
					print('Please enter a valid duration that is greater than 0 and less than 1')
					print('')

		# sort the data frame by phase (i.e., -0.25 to 1.25)
		theDf = theDf.sort_values('Phase')

		# The primary eclipse is centered near phase = 0, so given the eclipse duration (dur) the primary eclipse
		# data points are between -dur/2 and +dur/2 
		primary_eclipse_1 = theDf.loc[theDf.loc[:, 'Phase'] < float(dur)/2]
		primary_eclipse = primary_eclipse_1.loc[primary_eclipse_1.loc[:, 'Phase'] > -float(dur)/2]

		# re-order the index starting at 0
		primary_eclipse.reset_index(drop=True, inplace=True)    

		# min_dp is the index of the minima of the eclipse, i.e., maximum value since magnitude scale is inverted
		min_dp = primary_eclipse.mag.idxmax()   

		# initialize variable for the offset that will be returned
		offset = 0                              

		# flag variable will signal when to break out of loop once match is found	
		flag = 0                                

		# mk_1 will hold the row location for the first match of the pair and mk_2 will do the same for the second match
		mk_1 = 0                                 
		mk_2 = 0                                

		# check data points from index 0 (start of eclipse) up to the index of the minima (i.e., the left descending side of the eclipse)
		for i in range(0, min_dp + 1):         
			if flag == 1:  break

			# for each point on the left descending of the eclipse, check every point on the right ascending side
			for j in range(0, len(primary_eclipse.index) - min_dp): 
				if flag == 1: break
				mag_diff = abs(primary_eclipse.iloc[i][1] - primary_eclipse.iloc[-j-1][1])

				# if the difference in mag is this small, you've found matching points on both sides
				if mag_diff < 0.02:    
					offset = primary_eclipse.iloc[i][5] + \
					((primary_eclipse.iloc[len(primary_eclipse.index) - j - 1][5] - primary_eclipse.iloc[i][5])/2)
					mk_1 = i
					mk_2 = len(primary_eclipse.index) - j - 1
					flag = 1

		if offset == 0:
			print('No match found')

		# Plot the eclipse portion of the light curve with the selected points highlighted in yellow with a red line between them
		fig, ax = plt.subplots()
		ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
		plt.scatter(primary_eclipse['Phase'], primary_eclipse['mag'])
		plt.scatter(primary_eclipse.iloc[mk_1][5], primary_eclipse.iloc[mk_1][1], color='yellow')
		plt.scatter(primary_eclipse.iloc[mk_2][5], primary_eclipse.iloc[mk_2][1], color='yellow')
		plt.gca().invert_yaxis()
		plt.ylabel('Ic-mag')
		plt.xlabel('Phase')
		plt.title('Red line should appear half-way between two yellow points')
		plt.axvline(x=offset, color='red')                          # plot vertical line halfway between chosen data points
		plt.grid()
		
		if autoc == '1':
			satisfactory = '1'
		if autoc != '1':
			plt.show()
			satisfactory = input('Is the location of the vertical offset line satisfactory? [1]=Yes or [any other '
			'key]=No ').strip()
			print('')
		if satisfactory == '1':
			break
	return offset


if __name__ == '__main__':
	main()
