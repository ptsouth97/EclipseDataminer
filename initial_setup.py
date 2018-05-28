#!/usr/bin/python3.6

import pandas as pd


def main():
	'''testing'''

	print('testing...')
	set_up_df()


def read_query():
	'''Read the query file, create a new dataframe (df), and extract initial parameters'''
 
	head = ['Field', 'StarID', 'StarCat', 'RA', 'Decl', 'Pgood', 'I', 'Isig', 'Imed', 'Imederr']

	# read the query file and create a new dataframe -- init_df
	while True:
		try:
			if __name__ == '__main__':
				txt_file = 'query_2017-10-18_19_39_03.txt'
			else:
				txt_file = input('Enter the query text file name: ')

			init_df = pd.read_csv(txt_file, comment='#', sep='\s+', header=None, names=head)
			break

		except ValueError:
			print('Sorry, that file does not exist. Please try again')
			print('')
 

	tot = len(init_df)
	print('There are {} objects in the query file'.format(str(tot)))
	print('')

	# defining the starting point allows users to split large files into multiple sessions
	begin = int(input('Which object do you want to start on? '))
	print('')

	# the 'dist' parameter can be configured to determine if an object has already been classified
	dist = int(input('What distance in arcmin would you like to use to decide if the object is already classified? '))
	print('')

	# The fully automatic mode selects the default for all choices while they can be tweaked in the user input mode
	# FULLY AUTOMATIC FEATURE IS NOT FUNCTIONING YET
	auto = input('Do you want to run the analysis [1] fully automated or [any other key] with user input? ').strip()

	# REMOVE THIS ONCE FULLY AUTOMATIC FEATURE IS WORKING:
	if auto == '1':
		print('Sorry, fully automated is not available at this time. Defaulting to user input mode.')
		print('')
		auto_choice = '2'

	return init_df, tot, begin, dist, auto
 

if __name__ == '__main__':
	main()
