import pandas as pd
import numpy as np
from auxfunction_tablecreation import create_table_df

'''
@Author Anand Chitale
Reads in alternative_treatment_decision file in order to produce
decision stats on actions of the FOMC when presented with every observed
set of actions
'''
def main():
    df = pd.read_csv("../output/alternative_treatment_decisions.csv")

    df = df[df.columns[1:]]
    df = df[df.statement_policy_action.notnull()]
    df = df[df.bluebook_treatment_alt_a.notnull()]
    df['policy_options'] = df.apply(lambda row: get_policy_options(row),axis=1)
    #print(df)
    pivot = pd.pivot_table(data=df,index="policy_options",columns="statement_policy_action",
                           values="end_date",aggfunc=np.count_nonzero,fill_value=0)
    pivot = pivot.reset_index()
    pivot.rename(columns={"policy_options": "policy menu"}, inplace=True)
    pivot = pivot.append({'policy menu': 'Total', 'E': pivot['E'].sum()\
                          ,'T': pivot['T'].sum(),'U': pivot['U'].sum()\
                          }, ignore_index=True)
    print(pivot.columns)
    print(pivot)

    create_table_df(pivot,"tab_policy_alternative_decisions")
    
def get_policy_options(row):
    policy_options = []
    for alternative in ['bluebook_treatment_alt_a','bluebook_treatment_alt_b','bluebook_treatment_alt_c']:
        if str(row[alternative]) in ['U','T','E','?']:
            policy_options += (row[alternative])
    policy_options = sorted(policy_options)
    return ' '.join(policy_options)


main()