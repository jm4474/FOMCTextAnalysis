import pandas as pd
from numpy import isnan
'''
@Author Anand Chitale
Reads in the final derived file in order to find 
bluebook treatments, and then compares with statement outcome data
in order to determine which alternative was chosen at each meeting
'''


def main(): 
    derived_df = pd.read_csv("../../../derivation/python/output/meeting_derived_file.csv")
    alternative_df = extract_alternative_df(derived_df)
    ffr_df = get_ffr(1988,2008)
    merged_df = merge_ffr_alt_and_dec(ffr_df,alternative_df)
    #print(merged_df)
    merged_df.to_csv("../output/fed_targets_with_alternatives.csv")
    
    # Process missing alternatives

    bb_missing_df=pd.read_excel("../data/bluebook_missingalternatives.xlsx")
    bb_missing_df['start_date'] = pd.to_datetime(bb_missing_df['date'])
    
    bb_pivot = bb_missing_df.pivot(index = 'start_date', columns ='alt' , values =['text', 'change'])
    bb_pivot = bb_pivot.reset_index()
    
    new_cols = ['%s_%s' % (a, b if b else '') for a, b in bb_pivot.columns]
    bb_pivot.columns = ['start_date'] + new_cols[1:] 
    
    bb_pivot = bb_pivot.merge(merged_df,on='start_date',how='inner')
    bb_pivot=bb_pivot[['start_date','date', 'ffrtarget',
                       'target_before', 'target_after', 'decision',
                       'text_a', 'text_b', 'text_c', 
                       'text_d', 'change_a','change_b', 'change_c', 'change_d']]
    
    ren_dict = dict(zip(['change_a','change_b', 'change_c', 'change_d'],['bluebook_treatment_size_alt_a',
                                     'bluebook_treatment_size_alt_b',
                                     'bluebook_treatment_size_alt_c',
                                     'bluebook_treatment_size_alt_d']))
    
    text_dict = dict(zip([f"text_{alt}" for alt in ['a','b','c','d']],[f"alt {alt} corpus" for alt in ['a','b','c','d']]))
    
    bb_pivot.rename(columns=ren_dict ,inplace=True)
    bb_pivot.rename(columns=text_dict ,inplace=True)
    
    for alt in ['a','b','c','d']:
        bb_pivot[f"alt_{alt}_rate"] = bb_pivot['target_before'] - bb_pivot[f'bluebook_treatment_size_alt_{alt}']
        bb_pivot[f'alt {alt} corpus'] = bb_pivot[f'alt {alt} corpus'].apply(lambda text : f"[{text}]")
    
    bb_pivot.to_csv("../output/fed_targets_with_alternatives_missinbb.csv")

    
    

def get_ffr(startyear,endyear):
    ffr=pd.read_excel("../../../collection/python/data/FRED_DFEDTAR.xls",skiprows=10)
    ffr.rename(columns={"observation_date":"date","DFEDTAR":"ffrtarget"},inplace=True)
    ffr['year']=ffr['date'].apply(lambda x: x.year)
    ffr=ffr[(ffr['year']>=startyear) & (ffr['year']<=endyear)]
    ffr['target_before'] = ffr['ffrtarget'].shift(1)
    ffr['target_after'] = ffr['ffrtarget'].shift(-1)
    #print(ffr)
    return ffr

def merge_ffr_alt_and_dec(ffr,alternatives):
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

    alternatives = alternatives[['start_date','end_date','alt_a','alt_b',
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
    df_merge["decision"] = df_merge["target_after"]-df_merge["target_before"]
    df_merge = df_merge[['start_date','date','ffrtarget','target_before',
                         'target_after',"decision",
                         'alt_a_rate','alt_b_rate','alt_c_rate',
                         'alt_d_rate','alt_e_rate',
                         'bluebook_treatment_size_alt_a',
                         'bluebook_treatment_size_alt_b',
                         'bluebook_treatment_size_alt_c',
                         'bluebook_treatment_size_alt_d',
                         'bluebook_treatment_size_alt_e',
                         ]]
    return df_merge
def extract_alternative_df(df):
    df['end_date'] = pd.to_datetime(df['end_date'])
    df['start_date'] = pd.to_datetime(df['start_date'])
    sub_df = df[['start_date','end_date', 'event_type', 'bluebook_treatment_alt_a', 'bluebook_treatment_size_alt_a',
                 'bluebook_treatment_alt_b', 'bluebook_treatment_size_alt_b', 'bluebook_treatment_alt_c',
                 'bluebook_treatment_size_alt_c',
                 'bluebook_treatment_size_alt_d','bluebook_treatment_alt_d',
                 'bluebook_treatment_size_alt_e','bluebook_treatment_alt_e',
                 'statement_policy_change','statement_policy_action']]

    sub_df = sub_df[sub_df.event_type=="Meeting"]
    sub_df = sub_df[(sub_df.end_date.dt.year>=1988) & (sub_df.end_date.dt.year<=2008)]
    sub_df.loc[sub_df['statement_policy_action']=="unchanged","statement_policy_action"] = "U"
    sub_df.loc[sub_df['statement_policy_action']=="easing","statement_policy_action"] = "E"
    sub_df.loc[sub_df['statement_policy_action']=="tightening","statement_policy_action"] = "T"
    sub_df['alternative_treatment_chosen'] = ''
    sub_df['alternative_treatment_chosen'] = sub_df.apply(lambda row: get_alternative_treatment_outcome(row),axis=1)
    sub_df['alternative_treatment_size_chosen'] = ""
    sub_df['alternative_treatment_size_chosen'] = sub_df.apply(lambda row:get_alternative_treatment_size_outcome(row),axis=1)
    return sub_df.fillna("")
    
def get_alternative_treatment_outcome(row):
    if not isinstance(row['statement_policy_action'], str):
        return ""
    alternatives = ['alt_a','alt_b','alt_c','alt_d','alt_e']
    result = []
    for alternative in alternatives:
        treat_col = "bluebook_treatment_"+alternative
        if isinstance(row[treat_col],str)\
                and (row[treat_col] == row['statement_policy_action']):
            result.append(alternative)
    else:
        return " and ".join(result)

def get_alternative_treatment_size_outcome(row):
    if isnan(row['statement_policy_change']):
        return ''
    try:
        statement_size= float(row['statement_policy_change'])/100
    except:
        return ""
    results = []
    alternatives = ['alt_a', 'alt_b', 'alt_c','alt_d','alt_e']
    for alternative in alternatives:
        try:
            alternative_size = float(row["bluebook_treatment_size_"+alternative])
            if alternative_size == statement_size:
                results.append(alternative)
        except:
            continue

    return " and ".join(results)

main()
