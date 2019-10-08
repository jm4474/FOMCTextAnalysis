"""
Purpose: Summarizes the alternatives of the bluebooks as E,U,T and 
        produces the tab_sumstats_menu.tex table
Status: Final -- 08/19/2019
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import numpy as np


###############################################################################


def main():    
    sample_startdate=datetime.datetime(1989, 7, 1)
    sample_enddate=datetime.datetime(2006, 2, 1)
    data=load_bluebook_data(sample_startdate,sample_enddate)
    create_totstat(data,'tab_sumstats_menu')
    
def create_totstat(data,name):
    sum_menu=pd.pivot_table(data,values='end_date',index='treatment_options',aggfunc=np.count_nonzero,fill_value=0)
    sum_menu=sum_menu.reset_index()
    sum_menu.rename(columns={"end_date":"count"},inplace=True)
    sum_menu.loc[:,'len_count']=sum_menu["treatment_options"].apply(lambda x:len(x))
    sum_menu=sum_menu.sort_values(by='len_count')
    sum_menu=sum_menu.append({'treatment_options':'Total','count':sum_menu['count'].sum()},ignore_index=True)    
    ### Export the dataframe to latex
    # Dictionary for column headers
    headers={"treatment_options":"Policy Options","count":"Number of Meetings"}
    sum_menu.rename(columns=headers,inplace=True)
    sum_menu.drop(columns="len_count",inplace=True)    
    create_table_df(sum_menu,name)
    #print("Table",name,"is written." )


def create_table_df(data,name):
    columnheaders=list(data.columns)
    numbercolumns=len(columnheaders)
    
    with open("../../output/overleaf_files/"+name+".tex", "w") as f:
        f.write(r"\begin{tabular}{"+"l" + "".join("c" * (numbercolumns-1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write("\\addlinespace"+" \n")
        f.write(" & ".join([str(x) for x in columnheaders]) + " \\\ \n")    
        f.write("\\hline \n")
        # write data
        for idx,row in data.iterrows():
            # Do formatting for specific tables 
            if row.iloc[0]=="Total":
                f.write("\\addlinespace"+" \n")
            
            f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")   
    
        f.write("\\hline \n")
        f.write(r"\end{tabular}")

    
def load_bluebook_data(sample_startdate,sample_enddate):
    data=pd.read_excel("../../data/bluebook_manual_data_online_WORKING.xlsx")
    data['year']=data['start_date'].apply(lambda x : x.year)
    data=data[(data['start_date']>=sample_startdate) & (data['start_date']<=sample_enddate)]
    data=data.reset_index()
    
    treatments=[]    
    for alt in ['a','b','c','d','e']:
        try:
            treatments+=data['C_TREATMENT_alt_'+alt].unique().tolist()
        except:
            pass
            #print('No option found')
    treatments=list(set(treatments))
    
    data.loc[:,'treatment_options']=np.nan
    for idx,row in data.iterrows():
        treatments=[]    
        for alt in ['a','b','c','d','e']:
            try:
                treatments+=row['C_TREATMENT_alt_'+alt]
            except:
                pass
                #print('No option found')
        
        notvalid_treatments=['N']
        treatments=[x for x in treatments if not x in notvalid_treatments]
        treatment_tuple=tuple(set(treatments))
        treatments=",".join(list(set(treatments)))
        #print(treatments)
        #print(idx)
        if not len(treatment_tuple)==0:
            data['treatment_options'].iloc[idx]=treatments
        else:
            pass
    return data


if __name__ == "__main__":
   main()