# EclipseDataminer

This application's purpose is to analyze astronomical objects photometry measurements from a dataset to determine if the object is an eclipsing binary star.

## Workflow ##
* User must indepedently locate a suspected eclipsing binary in the [OGLE II photometry database](http://ogledb.astrouw.edu.pl/~ogle/photdb/)
* The coordinates of the suspect are entered in decimal hours and decimal degrees
* The application checks the [AAVSO's Variable Star Index (VSX)](https://www.aavso.org/vsx/) to check if there is already a variable at that location
* If not, data from the OGLEII database is downloaded to a dataframe and plotted as HJD vs magnitude
* Next, a frequency search is performed using the [Lomb-Scargle module from Astropy](http://docs.astropy.org/en/stable/stats/lombscargle.html)
* After the frequency is found, the folded light curve (phase plot) is generated
* The primary eclipse minima is set to phase zero and all other points are adjusted accordingly
* The phase plot is extended from 0-to-1 to -0.75 to 1.25 in order to show the full behavior of the eclipse
* A more precise estimate of the primary minima is determined by examining a close up and adjusting the zero-phase position
* All plots and data are saved to the working directory

## Examples ##

The program can be tested using these known eclipsers from the OGLE database:
* [OGLEII DIA BUL-SC43 V840](https://www.aavso.org/vsx/index.php?view=detail.top&oid=409515)
* [OGLEII BUL-SC01 V1070](https://www.aavso.org/vsx/index.php?view=detail.top&oid=356262)
* [OGLEII BUL-SC10 164819](https://www.aavso.org/vsx/index.php?view=detail.top&oid=356102)
