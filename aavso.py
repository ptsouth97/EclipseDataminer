#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup


def main():
	'''main function for testing this module'''

	print('TESTING...')
	print('')
	ra = 272.417942
	dec = -32.556141
	how_close = 1
	check_vsx(ra, dec, how_close)


def check_vsx(RA, DEC, close) -> object:
	'''Takes the objects coordinates and checks VSX to see if there is already an identified object at that location'''

	# create a string with the given coordinates
	coords = str(RA) + '+' + str(DEC)

	# concatenate the base url with the coordinates
	url = 'http://www.aavso.org/vsx/index.php?view=results.get&format=d&order=9&coords=' + coords
	print('Coordinates =  ' + coords)
	print('')

	# get the html data from the url
	r = requests.get(url)
	html_doc = r.text
	soup = BeautifulSoup(html_doc, 'lxml')
	    
	# grab the relevant object info in the 10th table
	table = soup.find_all('table')[10]                                  

	# find all the <tr> (i.e., rows of cells) in the table and get the first entry
	all_tr = table.find_all('tr')                                       # type = bs4.ResultSet
	first_entry = all_tr[2]                                             # type = bs4.Tag
	second_entry = all_tr[1]
   
	# convert the result into a string and slice the distance (dist) and object name (idx)
	results = first_entry.get_text().lstrip(' ')                        
	dist = float(results[3:7])
	idx = results[11:37].strip()
	var_type = results[67:71].strip()

	# if no objects are found nearby, make 'answer' = '1' and proceed with analysis
	if results[3:8] == 'There':
		print('No nearby objects were found')
		print('')
		print('PROCEEDING WITH ANALYSIS...')
		answer = '1'

	# if objects are found do 1 of 2 things:
	else:
		print('The VSX object {} of type {} is located {} arcmin from the coordinates you entered'.format(idx, var_type, dist))
		print('')
		# 1) if the nearby object is within the specified distance, assume its the same object and move on
		if dist < close:
			answer = '0'
			print('MOVING TO NEXT OBJECT...')
		# 2) if the nearby object is NOT within the specified distance, assume its a different object and proceed
		else:
			answer = '1'
			print('PROCEEDING WITH ANALYSIS...')
        
	print('')
	# returns 1 if no nearby objects found within specified distance; otherwise 0
	return answer


if __name__ == '__main__':
	main()
