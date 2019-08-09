import pandas as pd
from numpy import isnan
from auxfunction_tablecreation import create_table_df
'''
@Author Anand Chitale
Reads in the final derived file in order to find 
bluebook treatments, and then compares with statement outcome data
in order to determine which alternative was chosen at each meeting
'''
def main():
    full_df = pd.read_csv("../../../derivation/python/output/final_derived_file.csv")
    extract_alternative_df(full_df)
    
def extract_alternative_df(df):
    df['end_date'] = pd.to_datetime(df['end_date'])
    sub_df = df[['end_date', 'event_type', 'bluebook_treatment_alt_a', 'bluebook_treatment_size_alt_a',
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
    sub_df.to_csv("../output/alternative_treatment_decisions.csv")
    
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