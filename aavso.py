import requests
from bs4 import BeautifulSoup

def main():
    check_vsx()


def check_vsx(RA, DEC, close) -> object:
    '''Checks coordinates in VSX to see if there is already an identified object at that location'''

    coords = str(RA) + '+' + str(DEC)

    url = 'http://www.aavso.org/vsx/index.php?view=results.get&format=d&order=9&coords=' + coords
    print('Coordinates =  ' + coords)
    print('')
    r = requests.get(url)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'lxml')
    table = soup.find_all('table')[10]                                  # grab the table with the relevant object info

    all_tr = table.find_all('tr')                                       # type = ResultSet
    first_entry = all_tr[2]                                             # type = Tag
    results = first_entry.get_text().lstrip(' ')                        # type = string
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
    # answer = input('Do you wish to proceed? [1]=Yes, [any other key]=No ').strip()
    
    print('')
    return answer


if __name__ == '__main__':
	main()
