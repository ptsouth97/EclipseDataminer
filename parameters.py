import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import pandas as pd


def find_min(dtn, fully_auto):
    '''Finds and returns the average value near eclipse minima to control for measurement error'''

    dtn = dtn.loc[dtn.loc[:, 'Phase'] < 0.01]
    dtn = dtn.loc[dtn.loc[:, 'Phase'] > -0.01]
    avg = round(dtn['mag'].mean(), 2)

    fig, ax = plt.subplots()
    ax.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))
    plt.scatter(dtn['Phase'], dtn['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('Ic-mag')
    plt.xlabel('Phase')
    plt.title('Red line should appear at average of data points')
    plt.axhline(y=avg, color='red')  # plot horizontal line at the average near minima

    plt.grid()
    if fully_auto != '1':
        plt.show()

    return avg


def find_max(dfx, full_auto):
    dfx = dfx.loc[dfx.loc[:, 'Phase'] < 0.26]
    dfx = dfx.loc[dfx.loc[:, 'Phase'] > 0.24]
    av = round(dfx['mag'].mean(), 2)

    plt.scatter(dfx['Phase'], dfx['mag'])
    plt.gca().invert_yaxis()
    plt.ylabel('Ic-mag')
    plt.xlabel('Phase')
    plt.title('Red line should appear at average of data points')
    plt.axhline(y=av, color='red')  # plot horizontal line at the average near minima
    plt.grid()
    if full_auto != '1':
        plt.show()

    return av
