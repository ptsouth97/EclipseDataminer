#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup


def main():
	'''main loop for testing'''

	ra = 272.417942
	dec = -32.556141
	how_close = 1
	check_vsx(ra, dec, how_close)


def check_vsx(RA, DEC, close) -> object:
	'''Checks coordinates in VSX to see if there is already an identified object at that location'''

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
    
	# convert the result into a string and slice the distance (dist) and object name (idx)
	results = first_entry.get_text().lstrip(' ')                        
	dist = float(results[3:7])
	idx = results[11:37].strip()

	if results[3:8] == 'There':
		print('No nearby objects were found')
		print('')
		print('PROCEEDING WITH ANALYSIS...')
		answer = '1'

	else:
		print('The VSX object {} is located {} arcmin from the coordinates you entered'.format(idx, dist))
		print('')
		if dist < close:
			answer = '0'
			print('MOVING TO NEXT OBJECT...')
		else:
			answer = '1'
			print('PROCEEDING WITH ANALYSIS...')
        
	print('')
	# returns 1 if no nearby objects found within specified distance; otherwise 0
	return answer


if __name__ == '__main__':
	main()
