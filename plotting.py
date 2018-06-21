#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
import os


def main():
	'''main function for unit testing'''

	os.chdir('./test_folder')
	test = pd.read_csv('test_dat.csv')
	name = 'Test'
	auto = '2'
	plot_raw_data(test, name, auto)
 

def plot_raw_data(df, nme, ac):
	'''plots the raw data as a test to ensure data was imported properly'''

	fig, ax = plt.subplots()
	ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
	
	plt.scatter(df['HJD'], df['mag'], color='black', s=5)  # 's' is for marker size

	plt.gca().invert_yaxis()
	plt.title(nme + ' Raw Data')
	plt.xlabel('HJD')
	plt.ylabel('mag')
	plot_name = nme + '_Raw_Data.png'
	plt.savefig(plot_name)
	if ac != '1':
		plt.show()


def final_phase_diagram(phase_d, nm, per, a_c):
	''' plots the final phase diagram'''

	fig, ax = plt.subplots()
	ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
	plt.scatter(phase_d['Phase'], phase_d['mag'], color='black', s=5)    # 's' is for marker size
	plt.gca().invert_yaxis()
	plt.ylabel('Ic-mag')
	plt.xlabel('Phase')
	plt.title(nm + ' (P = ' + str(per) + ' d)')
	plt.grid()
	plt_name = nm + '_Phase_Diagram'
	plt.tight_layout()
	plt.savefig(plt_name)
	if a_c != '1':
		plt.show()

	return

	
if __name__ == '__main__':
	main()
