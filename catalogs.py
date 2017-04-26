import requests
from bs4 import BeautifulSoup

def main():
    check_vsx()


def check_vsx() -> object:
    '''Checks coordinates in VSX to see if there is already an identified object at that location'''

    while True:
        ra = input("What is the object's RA in decimal hours? ").strip()         # test value:  ra = '17.473532'
        if float(ra) <= 24 and float(ra) >= 0:
            break
        else:
            print('Please enter a valid RA between 0 and 24 decimal hours')

    while True:
        DEC = input("What is the object's DEC in decimal degrees? ").strip()  # test value:  DEC = '-40.22071'
        if float(DEC) <= 90 and float(DEC) >= -90:
            break
        else:
            print('Please enter a valid DEC between -90 and 90 decimal degrees')

    RA = float(ra) * 360 / 24  # convert to decimal degrees
    coords = str(RA) + '+' + DEC

    url = 'http://www.aavso.org/vsx/index.php?view=results.get&format=d&order=9&coords=' + coords
    print('Checking coordinates in VSX...')
    print('')
    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'lxml')
    table = soup.find_all('table')[10]                                  # grab the table with the relevant object info

    all_tr = table.find_all('tr')                                       # type = ResultSet
    first_entry = all_tr[2]                                             # type = Tag
    results = first_entry.get_text().lstrip(' ')                        # type = string
    dist = results[3:7]
    id = results[11:37].strip()

    if results[3:8] == 'There':
        print('No nearby objects were found')
    else:
        print('The VSX object {} is located {} arcmin from the coordinates you entered'.format(id, dist))
    print('')
    answer = input('Do you wish to proceed? [1]=Yes, [any other key]=No ').strip()
    print('')
    return answer, RA, DEC


def check_VizieR():
    '''checks SIMBAD database for cross-IDs'''
    pass

if __name__ == '__main__':
	main()