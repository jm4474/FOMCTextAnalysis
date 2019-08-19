
"""
Purpose: Produce summary statistics for the statements
Status: Draft
@author: olivergiesecke
"""


import pandas as pd
import numpy as np
from auxfunction_tablecreation import create_table_df      

data_df=pd.read_csv('../../../../derivation/python/output/final_derived_file.csv')

# Restrict to period (inclusive)
start_year=1988
end_year=2008
data_df=data_df[(data_df['year']>=start_year) & (data_df['year']<=end_year)]


pivot=pd.pivot_table(data_df,index='d_statement',values='start_date',columns='year',aggfunc=np.count_nonzero,fill_value=0)
pivot=pivot.reset_index()

pivot.rename(columns={"d_statement":"Available statement"},inplace=True)
pivot.replace({"Available statement":{False:"No",True:"Yes"}},inplace=True)

addline={"Available statement":"Total"}
for item in list(pivot.columns)[1:]:
    addline.update({item:pivot[item].sum() })

pivot=pivot.append(addline,ignore_index=True)

create_table_df(pivot,'tab_sumstats_statements',11)

