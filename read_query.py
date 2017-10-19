#!/usr/bin/python3.5

import pandas as pd


def main():
	file = 'query_2017-10-18_19_39_03.txt'
	load_query(file)


def load_query(txt):
	head = ['Field', 'StarID', 'StarCat', 'RA', 'Decl', 'Pgood', 'I', 'Isig', 'Imed', 'Imederr']
	data = pd.read_csv(txt, comment='#', sep='\s+', header=None, names=head)
	return data


'''def get_url(data):

	for obj in range(0, len(data)):
		name = data.iloc[obj][0].lower() + '_i_' + str(data.iloc[obj][1]) + '.dat'
		base = 'http://ogledb.astrouw.edu.pl/~ogle/photdb/data//'
		url = base + name
		print(url)
		exit = input('enter [1] to exit ').strip()
		
		if exit == '1':
			break
'''

if __name__ == '__main__':
	main()
