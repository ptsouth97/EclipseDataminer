#!/usr/bin/python3

import os
import pandas as pd
from sys import platform
import requests
from bs4 import BeautifulSoup


def main():
	''' main function for testing this module only'''

	nme = 'field=BUL_SC7&starid=362538&db=DIA&points=good'
	get_data_from_web(nme)


def set_name(field, star_id):
	'''store basic information about the object of interest'''
    
	path_id = 'OGLEII_' + field + '_' + star_id
	url_id = 'field={}&starid={}&db=DIA&points=good'.format(field, star_id)

	print('The ID is: ' + path_id + ' and the url_id is ' + url_id)
	print('')

	return path_id, url_id


def make_folder(path_id):
	'''set up a new folder for the object's files and create a new dataframe to store the object info'''
	
	# get the correct path
	if platform == 'linux':
		newpath = os.getcwd() + '/' + path_id
	else:
		newpath = os.getcwd() + '\\' + path_id
 
	# set up new directory with the name of the object
	if not os.path.exists(newpath):
		os.makedirs(newpath)                    

    # create new data frame that will hold the information discovered
	columns = ['name', 'period', 'epoch', 'minimum', 'maximum']
	new_df = pd.DataFrame(columns=columns, index=range(0, 1))

	return new_df, newpath


def get_data_from_web(the_name):
	'''Takes the object name and returns a .dat file with photometry data from OGLE database as a dataframe'''

	while True:    
		base = 'http://ogledb.astrouw.edu.pl/~ogle/photdb/getobj.php?'
		url = base + the_name
		print('The url is ' + url)
		r = requests.get(url)
		html_doc = r.text
		soup = BeautifulSoup(html_doc, 'lxml')
    
		try:
			table = soup.find('pre').contents[0]

		except AttributeError:
			print('***No good DIA photometry for this object***')
			print('')
			print('MOVING TO NEXT OBJECT...')
			df = pd.DataFrame(columns=['1', '2', '3'], index=range(0, 1))
			break

		long_str = table.split()
		col = ['HJD', 'mag', 'mag_err', 'photometry_flag', 'frame_grade']
		total = len(long_str)
		rows = int(total / 5)
		df = pd.DataFrame(columns=col, index=range(0, rows))    

		for row in range(0, rows):
			for i in range(0, 5):
				df.iloc[row][i] = long_str[row * 5 + i]

		df = df.apply(pd.to_numeric, errors='ignore')
		df = df.loc[df['frame_grade'].isin(['A', 'B', 'C'])]
		df.to_csv('RAW_DATA.csv')
        
		break

	return df


if __name__ == '__main__':
	main()
