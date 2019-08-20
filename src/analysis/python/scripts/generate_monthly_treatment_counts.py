import pandas as pd
def main():
    alternatives = pd.read_csv("../output/fed_targets_with_alternatives.csv")
    alternatives = alternatives[alternatives.date!="2003-09-15"]
    treatments = alternatives.copy()

    treatments = treatments[['date',
                             'bluebook_treatment_size_alt_a',
                             'bluebook_treatment_size_alt_b',
                             'bluebook_treatment_size_alt_c',
                             'bluebook_treatment_size_alt_d',
                             'bluebook_treatment_size_alt_e'
                             ]]
    treatments.rename(columns={'bluebook_treatment_size_alt_a':'tsa',
                               'bluebook_treatment_size_alt_b':'tsb',
                               'bluebook_treatment_size_alt_c':'tsc',
                               'bluebook_treatment_size_alt_d':'tsd',
                               'bluebook_treatment_size_alt_e': 'tse',

                               },inplace=True)
    for alt in ['a','b','c','d','e']:
        treatments['ts'+alt] = pd.to_numeric(treatments['ts' + alt], errors='coerce')

    treatments['d_dec'] = ((treatments['tsa'] < 0)|
                           (treatments['tsb'] < 0)|
                           (treatments['tsc'] < 0)|
                           (treatments['tsd'] < 0)|
                           (treatments['tse'] < 0)).astype(int)

    treatments['d_unc'] = ((treatments['tsa'] == 0)|
                           (treatments['tsb'] == 0)|
                           (treatments['tsc'] ==  0)|
                           (treatments['tsd'] == 0)|
                           (treatments['tse'] == 0)).astype(int)

    treatments['d_inc'] = ((treatments['tsa'] > 0)|
                           (treatments['tsb'] > 0)|
                           (treatments['tsc'] > 0)|
                           (treatments['tsd'] > 0)|
                           (treatments['tse'] > 0)).astype(int)
    column_names = ['date','d_dec','d_unc','d_inc']
    sizes = [-0.75,-0.5,-.25,0,.25,.5,.75]
    for size in sizes:
        size_name = 'd_{sign}0{val}'.format(
            sign="m" if size < 0 else "", val=str(abs(int(size * 100)))).replace("00","0")
        treatments[size_name] = ((treatments['tsa']==size)|\
                                (treatments['tsb']==size)|\
                                (treatments['tsc']==size)|
                                (treatments['tsd'] == size)|
                                (treatments['tse'] == size)
                                 ).astype(int)
        column_names.append(size_name)



    treatments['month'] = pd.to_datetime(treatments.date).dt.month
    treatments['year'] = pd.to_datetime(treatments.date).dt.year

    column_names.append('month')
    column_names.append('year')
    treatments = treatments[column_names]
    month_df = pd.DataFrame()
    for year in range(1988,2009):
        for month in range(1,13):
            month_df = month_df.append({'month':month,'year':year},ignore_index=True)
    treatments = treatments.merge(month_df,on=['month','year'],how="outer").fillna(0)

    treatments.to_csv("../output/monthly_treatment_counts.csv")
if __name__ == "__main__":
    main()