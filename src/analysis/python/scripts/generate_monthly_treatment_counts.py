import pandas as pd
def main():
    alternatives = pd.read_csv("../output/alternative_treatment_decisions.csv")
    treatments = alternatives.copy()
    treatments = treatments[['end_date','bluebook_treatment_size_alt_a',
                             'bluebook_treatment_size_alt_b',
                             'bluebook_treatment_size_alt_c'
                             ]]
    treatments.rename(columns={"end_date":"date",'bluebook_treatment_size_alt_a':'tsa',
                               'bluebook_treatment_size_alt_b':'tsb',
                               'bluebook_treatment_size_alt_c':'tsc',
                               },inplace=True)

    column_names = ['month','year']
    sizes = [-0.75,-0.5,-.25,0,.25,.5,.75]
    for size in sizes:
        for alt in ['a','b','c']:
            treatments[str(size)+alt] = pd.to_numeric(treatments['ts'+alt],errors='coerce')==size
            treatments['d_dec_'+alt] = pd.to_numeric(treatments['ts'+alt],errors='coerce')<0
            treatments['d_unc_' + alt] = pd.to_numeric(treatments['ts' + alt],errors='coerce') == 0
            treatments['d_inc_' + alt] = pd.to_numeric(treatments['ts' + alt],errors='coerce') > 0

        size_name = 'd_{sign}0{val}'.format(
            sign="m" if size < 0 else "", val=str(abs(int(size * 100)))).replace("00","0")
        print(size_name)
        treatments[size_name] = treatments[[str(size)+'a',str(size)+'b',
                                            str(size)+'c']].sum(axis=1)
        treatments['d_dec'] = treatments[['d_dec_a','d_dec_b','d_dec_c']].sum(axis=1)
        treatments['d_unc'] = treatments[['d_unc_a','d_unc_b','d_unc_c']].sum(axis=1)
        treatments['d_inc'] = treatments[['d_inc_a','d_inc_b','d_inc_c']].sum(axis=1)

        column_names.append(size_name)
    column_names.append('d_dec')
    column_names.append('d_unc')
    column_names.append('d_inc')
    treatments['month'] = pd.to_datetime(treatments.date).dt.month
    treatments['year'] = pd.to_datetime(treatments.date).dt.year
    treatments = treatments[column_names]
    month_df = pd.DataFrame()
    for year in [1988,2009]:
        for month in [1,13]:
            month_df = month_df.append({'month':month,'year':year},ignore_index=True)
    treatments = treatments.astype(bool).astype(int)
    treatments = treatments.merge(month_df,on=['month','year'],how="outer").fillna(0)
    print(treatments)
    treatments.to_csv("../output/monthly_treatment_counts.csv")
if __name__ == "__main__":
    main()