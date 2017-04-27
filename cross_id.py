from astroquery.vizier import Vizier
import astropy.coordinates as coord
import astropy.units as u


def main():
    '''main loop for unit testing with sample coordinates'''

    right_ascension = 262.103           # 272.279
    declination =  -40.22071            # -26.63787
    field_name = 'BUL'
    viz(right_ascension, declination, field_name)


def viz(ra, dec, fn):
    '''Queries VizieR database for coordinates given and returns matches < 1 arcsec for given catalogs'''

    v = Vizier(columns=["*", "+_r"])        # '*' sort by columns, '+' for ascending, '_r' for distance column

    result = v.query_region(coord.SkyCoord(ra=ra, dec=dec,
                                                unit=(u.deg, u.deg),
                                                frame='icrs'),
                                                radius=1.0*u.arcsec,
                                                catalog=['J/AcA/52/129/catalog'])  # DIA OGLE2 candidate variable stars


    if str(result) == 'Empty TableList':
        nw_nm = 'Found nothing'

    else:
        r = float(result[0]['_r'])
        field = int(result[0]['Field'])
        vno = int(result[0]['Vno'])
        a_nm = 'OGLEII DIA ' + fn + '-SC' + str(field) + ' V' + str(vno)
        print('')
        print('Found ' + a_nm + ' at ' + str(r) + ' arcsec from coordinates')
        accept = input('Accept as cross match?  [1]=Yes, [any other key]=No ').strip()
        if accept == '1':
            nw_nm = a_nm

    return nw_nm

if __name__ == '__main__':
	main()

# 'II/246/out',              # 2MASS
# 'I/327/cmc15',             # CMC15
# 'I/322A/out',              # UCAC4
# 'I/284/out',               # USNO-B1.0
# 'I/317/sample',            # PPMXL
# 'B/vsx/vsx'])              # AAVSO VSX