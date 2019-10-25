import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
def main():
    data_ffr_and_alts = pd.read_csv("../../output/fed_targets_with_alternatives.csv")
    plot_target(data_ffr_and_alts)

def plot_target(dataffr):

    #dataffr[dataffr['year'] == 1990]

    ### Get turning points
    dataffr.reset_index(inplace=True)

    t_point = dataffr[dataffr['ffrtarget'].diff(1) != 0]
    #t_point[t_point['year'] == 2007]

    plt.rc('text', usetex=True)
    fig = plt.figure(figsize=(10, 3))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(dataffr['date'], dataffr['alt_a_rate'], 'bo',markersize=1)
    ax.plot(dataffr['date'], dataffr['alt_b_rate'], 'bo',markersize=1)
    ax.plot(dataffr['date'], dataffr['alt_c_rate'], 'bo',markersize=1)
    ax.plot(dataffr['date'], dataffr['alt_d_rate'], 'bo',markersize=1)
    ax.plot(dataffr['date'], dataffr['alt_e_rate'], 'bo',markersize=1,label="Policy Menu")

    ax.plot(dataffr['date'], dataffr['target_after'], 'yo', markersize=3,fillstyle='none',label="Target After Meeting")
    ax.legend(loc='upper right')
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)



    #turning_points = ['1989-06-01', '1993-06-01', '1995-04-01', '2000-11-01', '2004-01-01', '2007-02-01']
    #for datestring in turning_points:
    #    ax.axvline(x=pd.to_datetime(datestring), color='gray', linestyle='--')

    #plt.legend(['Federal Funds Alternatives and Actions'], frameon=False)
    plt.savefig('../../output/overleaf_files/fig_fed_target_and_alt.png', dpi=300, bbox_inches='tight')
    dataffr['decision'] = dataffr['target_after']-dataffr['target_before']
    dataffr.loc[168,'decision'] = -.5
if __name__ == "__main__":
    main()