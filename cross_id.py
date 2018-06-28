#!/usr/bin/python3

from astroquery.vizier import Vizier
import astropy.coordinates as coord
import astropy.units as u
import pandas as pd
import re


# DIA OGLE      'J/AcA/52/129'  [_r, Field, Vno, RAJ2000, DEJ2000, Rad, VType, NFrames, NGood, Flags]
# 2MASS         'II/246/out'    [_r, RAJ2000, DEJ2000, _2MASS, Jmag, Rf1g, Bf1g, Cf1g, Xf1g, Af1g]
# CMC15         'I/327/cmc15'   [_r, CMC15, RAJ2000, DEJ2000, r_mag, Nt, Jmag, Hmag, Ksmag]
# UCAC4         'I/322A/out'    [_r, UCAC4, RAJ2000, DEJ2000, ePos, f.mag, h, Z, B, L, N, S]
# USNO-B1.0     'I/284/out'     [_r, USNO-B1.0, RAJ2000, DEJ2000, e_RAJ2000, R1mag, B2mag, R2mag, Imag]
# PPMXL         'I/317/sample'  [_r, RAJ2000, DEJ2000, pmRA, pmDE, r1mag, r2mag, imag, No, f1]


def main():
	'''main loop for unit testing 'cross_id' with sample coordinates'''

	right_ascension = 272.381145	# 272.279
	declination = -32.42459			# -26.63787
	field_name = 'BUL'
	viz(right_ascension, declination, field_name)


def viz(ra, dec, fn):
	'''Queries VizieR database for coordinates given and returns matches < 1 arcsec for given catalogs'''

	nw_nm = 'Found nothing'

	# create new data frame that will hold the cross-id matches discovered
	columns = ['name', 'dist', 'ra', 'dec']
	matches = pd.DataFrame(columns=columns, index=range(0, 6))

	v = Vizier(columns=["**", "+_r"])        # '*' sort by columns, '+' for ascending, '_r' for distance column

	# query the database
	result = v.query_region(coord.SkyCoord(ra=ra, dec=dec,
                                                unit=(u.deg, u.deg),
                                                frame='icrs'),
                                                radius=1.0*u.arcsec,
                                                catalog=['J/AcA/52/129',
                                                         'II/246/out',
                                                         'I/327/cmc15',
                                                         'I/322A/out',
                                                         'I/284/out',
                                                         'I/317/sample'])

	for cat in range(0, int(len(result))):
		if str(result) == 'Empty TableList':
			break
        
		which_catalog = result[cat]
		r = float(which_catalog[0]['_r'])
		RA = float(which_catalog[0]['RAJ2000'])
		DE = float(which_catalog[0]['DEJ2000'])

		matches.iloc[cat][1] = r
		matches.iloc[cat][2] = RA
		matches.iloc[cat][3] = DE

		if bool(re.search('Field', str(result[cat].columns))) == True:
			field = int(result[cat]['Field'])
			vno = int(result[cat]['Vno'])
			nw_nm = 'OGLEII DIA ' + fn + '-SC' + str(field) + ' V' + str(vno)
			print('The new name is ' + nw_nm)
			matches.iloc[0][0] = nw_nm

		elif  bool(re.search('2MASS', str(result[cat].columns))) == True and \
                        bool(re.search('Rflg', str(result[cat].columns))) == True:
			mass_name_1 = str(result[cat]['_2MASS'])
			mass_name_2 = mass_name_1[33:50].strip()
			mass_name_3 = '2MASS J' + mass_name_2
			matches.iloc[cat][0] = mass_name_3

		elif  bool(re.search('CMC15', str(result[cat].columns))) == True:

			cmc_name_1 = str(result[cat]['CMC15'])
			cmc_name_2 = cmc_name_1[32:50].strip()
			cmc_name_3 = 'CMC15 J' + cmc_name_2
			matches.iloc[cat][0] = cmc_name_3

		elif  bool(re.search('UCAC4', str(result[cat].columns))) == True:

			uc_name_1 = str(result[cat]['UCAC4'])
			uc_name_2 = uc_name_1[22:60].strip()
			uc_name_3 = 'UCAC4 ' + uc_name_2
			matches.iloc[cat][0] = uc_name_3

		elif  bool(re.search('USNO-B1.0', str(result[cat].columns))) == True:

			usn_name_1 = str(result[cat]['USNO-B1.0'])
			usn_name_2 = usn_name_1[26:50].strip()
			usn_name_3 = 'USNO-B1.0 ' + usn_name_2
			matches.iloc[cat][0] = usn_name_3

		elif  bool(re.search('PPMXL', str(result[cat].columns))) == True:

			pm_name_1 = str(result[cat]['PPMXL'])
			pm_name_2 = pm_name_1[40:70].strip()
			pm_name_3 = 'PPMXL ' + pm_name_2
			matches.iloc[cat][0] = pm_name_3

	final_matches= matches.dropna(axis=0, how='any')

	if __name__ == '__main__':
		print('POSSIBLE MATCHES FOUND:')
		print(final_matches)

	return nw_nm, final_matches

if __name__ == '__main__':
	main()
