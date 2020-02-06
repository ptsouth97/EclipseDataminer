# EclipseDataminer

This application's purpose is to analyze astronomical objects' photometry measurements from a dataset to determine if the object is an [eclipsing binary star](http://www.physics.sfasu.edu/astro/ebstar/ebstar.html).
Tested with Python 3.5 running on Ubuntu

## Workflow ##
* User must indepedently download a text file with query information from the [OGLE II photometry database](http://ogledb.astrouw.edu.pl/~ogle/photdb/)
* initial_setup.py reads the query file, creates a dataframe, defines the size and starting point in the df, decides how close for a cross-id, and decides whether or not to run fully auto or with user input
* app_eclipseDataminer.py loops through each row and converts the coordinates of the suspect into decimal hours and decimal degrees
* aavso.py checks the [AAVSO's Variable Star Index (VSX)](https://www.aavso.org/vsx/) to check if there is already a variable at that location using a user defined distance
* If not, data from the OGLE II database is downloaded (URL must now be provided by user due to database encryption) to a dataframe and plotted as magnitude vs Julian date
* Next, a frequency search is performed by lombscargle.py using the [Lomb-Scargle module from Astropy](http://docs.astropy.org/en/stable/stats/lombscargle.html)
* After the frequency is found, the folded light curve (phase plot) is generated
* The primary eclipse minima is set to phase zero and all other points are adjusted accordingly
* The phase plot is extended from (0 to 1) to (-0.75 to 1.25) in order to show the full behavior of the eclipse
* A more precise estimate of the primary minima is determined by examining a close up and adjusting the zero-phase position
* Minimum and maximum values for the curve are calculated by averaging values near phase 0 and phase 0.25, respectively
* All plots and data are saved to the working directory
* The application also generates a .csv file with possible cross-identifications by querying [VizieR](http://vizier.u-strasbg.fr/cgi-bin/VizieR)

## Examples ##

The program can be tested using these known eclipsers from the OGLE database:
* [OGLEII BUL-SC48 144757](https://www.aavso.org/vsx/index.php?view=detail.top&oid=409584)
* [OGLEII DIA BUL-SC43 V840](https://www.aavso.org/vsx/index.php?view=detail.top&oid=409515)
* [OGLEII BUL-SC01 V1070](https://www.aavso.org/vsx/index.php?view=detail.top&oid=356262)
* [OGLEII BUL-SC10 164819](https://www.aavso.org/vsx/index.php?view=detail.top&oid=356102)
