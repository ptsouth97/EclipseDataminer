from astropy.stats import LombScargle
import matplotlib.pyplot as plt
import astropy.units as u
import numpy as np
import pandas as pd


def main():
    '''main loop for unit testing purposes'''

    n = 'Test Data'
    rand = np.random.RandomState(42)
    t = 100 * rand.rand(100)
    y = np.sin(2 * np.pi * t) + 0.1 * rand.randn(100)
    col_1 = pd.DataFrame(t)
    col_2 = pd.DataFrame(y)
    dt = pd.concat([col_1, col_2], axis=1)
    dt.columns = ['HJD', 'mag']
    find_freq(dt, n)


def find_freq(dt, n):
    '''Uses astropy's LombScargle method to search for frequency with the highest power and then visually check
    if it produces a viable phase plot.  For more see http://docs.astropy.org/en/stable/stats/lombscargle.html'''

    t = dt['HJD']
    t_days = t * u.day
    y = dt['mag']
    y_mags = y * u.mag

    while True:
        print('########################################')
        print('#           PERIOD ANALYSIS            #')
        print('########################################')
        print('')
        print('Lomb Scargle arguments set to default')
        print('')
        method = 'auto'
        numterms = 1
        nyq = 5
        spp = 5
        mod = 0

        while True:
            choice = input('Would you like to modify arguments for Lomb Scargle? [1]=Yes, [any other key]=No ')

            if choice.strip() == '1':
                print('')
                print('What do you want to do?')
                print('1 = Specify method')
                print('2 = Specify nterms')
                print('3 = Specify min & max frequency,')
                print('4 = Specify Nyquist factor')
                print('5 = Specify the frequency')
                print('')
                choice2 = input('What is your choice? ')

                # method
                if choice2.strip() == '1':
                    method = input("What method do you want to use? ('auto', 'fast', 'slow', 'cython', 'chi2', "
                                   "fastchi2', or 'scipy') ").strip().lower()

                # nterms
                if choice2.strip() == '2':
                    if method == 'chi2' or method == 'fastchi2':
                        numterms = int(input('How many Fourier terms do you want to use in the model? ').strip())
                    else:
                        print("Number of terms 'nterms' can only be modified for methods 'chi2' or 'fastchi2'")

                # min/max frequency
                if choice2.strip() == '3':
                    min_freq = float(input('What is the minimum frequency? ').strip())
                    max_freq = float(input('What is the maximum frequency? ').strip())
                    spp = float(input('How many samples per peak? ').strip())
                    mod = 1

                # Nyquist
                if choice2.strip() == '4':
                    nyq = int(input('What Nyquist factor do you want to try? '))
                    mod = 2
                    break

                # specific frequency
                if choice2.strip() == '5':
                    best_frequency = float(input('What frequency do you want to try? '))
                    mod = 3
                    break

            else:
                # frequency, power = LombScargle(t_days, y_mags, nterms=2).autopower(method='chi2')
                # power_sorted = power.argsort()
                # best_frequency = frequency[power_sorted[-2]]
                # best_frequency = frequency[np.argmax(power)]  # most likely frequency is where the power is highest
                break

        if mod == 0:
            frequency, power = LombScargle(t_days, y_mags, nterms=numterms).autopower(method=method)

        if mod == 1:
            frequency, power = LombScargle(t_days, y_mags, nterms=numterms).autopower(method=method,
                                                                                 minimum_frequency=min_freq,
                                                                                 maximum_frequency = max_freq,
                                                                                 samples_per_peak = spp)

        if mod == 2:
            frequency, power = LombScargle(t_days, y_mags).autopower(nyquist_factor=nyq)

        if mod == 3:
            frequency, power = LombScargle(t_days, y_mags).power(best_frequency)

        # power_sorted = power.argsort()
        # best_frequency = frequency[power_sorted[-1]]
        best_frequency = frequency[np.argmax(power)]  # the most likely frequency is where the power is highest
        plt.figure(1)
        plt.subplot(211)
        plt.plot(frequency, power, color='black')
        plt.axvline(x=best_frequency, color='blue', linestyle='dashed')  # plot vertical line at best frequency
        plt.xlabel('Frequency')
        plt.ylabel('Lomb-Scargle Power')
        plt.title('Frequency = ' + str(best_frequency))
        figname = n + 'Periodiagram'
        plt.savefig(figname)

        # create a new column in the dataframe to hold the phase values generated from the frequency
        dt.loc[:, 'Phase'] = dt.loc[:, 'HJD'].apply(lambda x: x*best_frequency%1)

        plt.subplot(212)
        plt.scatter(dt['Phase'], dt['mag'], color='black', s=5)  # 's' is for marker size
        plt.gca().invert_yaxis()
        plt.ylabel('Ic-mag')
        plt.xlabel('Phase')
        plt.show()
        print('')
        satisf = input('Is the phase plot satisfactory? [1]=Yes, [any other key]=No ').strip()
        print('')
        if satisf == '1':
            break
    return best_frequency, dt


if __name__ == '__main__':
	main()