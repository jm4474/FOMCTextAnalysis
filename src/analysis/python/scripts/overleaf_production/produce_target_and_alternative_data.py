import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
def main():
    data_ffr = get_ffr(1988, 2008)
    data_ffr_and_alts = get_alternatives(data_ffr)
    #print(data_ffr_and_alts)
    plot_target(data_ffr_and_alts)

def get_ffr(startyear,endyear):
    ffr=pd.read_excel("../../../../collection/python/data/FRED_DFEDTAR.xls",skiprows=10)
    ffr.rename(columns={"observation_date":"date","DFEDTAR":"ffrtarget"},inplace=True)
    ffr['year']=ffr['date'].apply(lambda x: x.year)
    ffr=ffr[(ffr['year']>=startyear) & (ffr['year']<=endyear)]
    ffr['target_before'] = ffr['ffrtarget'].shift(1)
    ffr['target_after'] = ffr['ffrtarget'].shift(-1)
    #print(ffr)
    return ffr

def get_alternatives(ffr):
    alternatives = pd.read_csv("../../output/alternative_treatment_decisions.csv")
    alternatives['alt_a'] = alternatives['bluebook_treatment_size_alt_a'].\
        apply(lambda x: pd.to_numeric(x,errors="coerce"))
    alternatives['alt_b'] = alternatives['bluebook_treatment_size_alt_b'].\
        apply(lambda x: pd.to_numeric(x,errors="coerce"))
    alternatives['alt_c'] = alternatives['bluebook_treatment_size_alt_c'].\
        apply(lambda x: pd.to_numeric(x,errors="coerce"))
    alternatives['alt_d'] = alternatives['bluebook_treatment_size_alt_d']. \
        apply(lambda x: pd.to_numeric(x, errors="coerce"))
    alternatives['alt_e'] = alternatives['bluebook_treatment_size_alt_e']. \
        apply(lambda x: pd.to_numeric(x, errors="coerce"))

    alternatives = alternatives[['end_date','alt_a','alt_b',
                                 'alt_c','alt_d','alt_e',
                                 'bluebook_treatment_size_alt_a',
                                 'bluebook_treatment_size_alt_b',
                                 'bluebook_treatment_size_alt_c',
                                 'bluebook_treatment_size_alt_d',
                                 'bluebook_treatment_size_alt_e'
                                 ]]
    alternatives['date'] = pd.to_datetime(alternatives['end_date'])
    df_merge = pd.merge(ffr,alternatives,on="date",how="right")
    df_merge['alt_a_rate'] = df_merge[['target_before','alt_a']].sum(axis=1,skipna=False)
    df_merge['alt_b_rate'] = df_merge[['target_before','alt_b']].sum(axis=1,skipna=False)
    df_merge['alt_c_rate'] = df_merge[['target_before','alt_c']].sum(axis=1,skipna=False)
    df_merge['alt_d_rate'] = df_merge[['target_before','alt_d']].sum(axis=1,skipna=False)
    df_merge['alt_e_rate'] = df_merge[['target_before','alt_e']].sum(axis=1,skipna=False)


    df_merge = df_merge[['date','ffrtarget','target_before',
                         'target_after',
                         'alt_a_rate','alt_b_rate','alt_c_rate',
                         'alt_d_rate','alt_e_rate',
                         'bluebook_treatment_size_alt_a',
                         'bluebook_treatment_size_alt_b',
                         'bluebook_treatment_size_alt_c',
                         'bluebook_treatment_size_alt_d',
                         'bluebook_treatment_size_alt_e',
                         ]]
    return df_merge

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

    dataffr.to_csv("../../output/fed_targets_with_alternatives.csv")
if __name__ == "__main__":
    main()