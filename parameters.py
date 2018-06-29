#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import pandas as pd
import os


def main():
	'''main function for testing this module'''

	os.chdir('./test_folder')
	df = pd.read_csv('test_dataframe.csv')
	find_min(df, 2)
	find_max(df, 2)


def find_min(dtn, fully_auto):
	'''Finds and returns the average value near eclipse minima to control for measurement error'''

	dtn = dtn.loc[dtn.loc[:, 'Phase'] < 0.01]
	dtn = dtn.loc[dtn.loc[:, 'Phase'] > -0.01]
	avg = round(dtn['mag'].mean(), 2)

	fig, ax = plt.subplots()
	ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
	plt.scatter(dtn['Phase'], dtn['mag'])
	plt.gca().invert_yaxis()
	plt.ylabel('Ic-mag')
	plt.xlabel('Phase')
	plt.title('Red line should appear at average of data points')
	plt.axhline(y=avg, color='red')  # plot horizontal line at the average near minima

	plt.grid()

	if fully_auto != '1':
		plt.show()

	return avg


def find_max(dfx, full_auto):
	'''finds the max'''

	dfx = dfx.loc[dfx.loc[:, 'Phase'] < 0.26]
	dfx = dfx.loc[dfx.loc[:, 'Phase'] > 0.24]
	av = round(dfx['mag'].mean(), 2)

	plt.scatter(dfx['Phase'], dfx['mag'])
	plt.gca().invert_yaxis()
	plt.ylabel('Ic-mag')
	plt.xlabel('Phase')
	plt.title('Red line should appear at average of data points')
	plt.axhline(y=av, color='red')  # plot horizontal line at the average near minima
	plt.grid()

	if full_auto != '1':
		plt.show()

	return av


def final_csv(frequency, adjustment, phased_df, choice):
	''' calculate relevant parameters, place in data frame, and then write to file'''

	period = round(1 / frequency, 4)
	epoch = round(epoch + period * adjustment, 3)
	minimum = find_min(phased_df, choice)
	maximum = find_max(phased_df, choice)
	final_df.iloc[0][0] = name
	final_df.iloc[0][1] = period
	final_df.iloc[0][2] = epoch
	final_df.iloc[0][3] = minimum
	final_df.iloc[0][4] = maximum
	final_df.to_csv(name + '_Parameters.csv')


if __name__ == '__main__':
	main()
