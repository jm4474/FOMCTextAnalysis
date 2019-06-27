"""
Purpose: Summarizes the alternatives of the bluebooks
Status: Draft
@author: olivergiesecke
"""

###############################################################################
### Set packages ###

import pandas as pd
import re
import os
import matplotlib.pyplot as plt


from nltk.corpus import stopwords
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models.phrases import Phrases, Phraser
# spacy for lemmatization
from distutils.core import setup
from Cython.Build import cythonize
import spacy
from wordcloud import WordCloud
import numpy as np


###############################################################################

data=pd.read_excel('../data/bluebook_data_for_online_WORKING.xlsx')
data['year']=data['start_date'].apply(lambda x: x.year)
data=data[data['year']>=1988]
data.reset_index(inplace=True)
# Get a list of treatments

treatments=[]    
for alt in ['a','b','c','d','e']:
    try:
        treatments+=data['C_TREATMENT_alt_'+alt].unique().tolist()
    except:
        print('No option found')
treatments=list(set(treatments))

data.loc[:,'treatment_options']=np.nan
for idx,row in data.iterrows():
    treatments=[]    
    for alt in ['a','b','c','d','e']:
        try:
            treatments+=row['C_TREATMENT_alt_'+alt]
        except:
            print('No option found')
    
    valid_treatments=['E','U','T']
    treatments=[x for x in treatments if x in valid_treatments]
    treatment_tuple=tuple(set(treatments))
    treatments=",".join(list(set(treatments)))
    if not len(treatment_tuple)==0:
        data['treatment_options'].iloc[idx]=treatments
    else:
        pass


sum_menu=pd.pivot_table(data,values='end_date',index='treatment_options',aggfunc=np.count_nonzero,fill_value=0)
sum_menu=sum_menu.reset_index()
sum_menu.rename(columns={"end_date":"count"},inplace=True)
sum_menu=sum_menu.append({'treatment_options':'Total','count':sum_menu['count'].sum()},ignore_index=True)

### Export the dataframe to latex
# Dictionary for column headers
headers={"treatment_options":"Policy Options","count":"Number of Meetings"}
sum_menu.rename(columns=headers,inplace=True)

create_table_df(sum_menu,'tab_sumstats_menu')

def create_table_df(data,name):
    columnheaders=list(data.columns)
    numbercolumns=len(columnheaders)
    
    with open("../output/"+name+".tex", "w") as f:
        f.write(r"\begin{tabular}{"+"l" + "".join("c" * (numbercolumns-1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write(" & ".join([x for x in columnheaders]) + " \\\ \n")    
        f.write("\\hline \n")
        # write data
        for idx,row in data.iterrows():
            # Do formatting for specific tables 
            if row.iloc[0]=="Total":
                f.write("\\addlinespace"+" \n")
            
            f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")   
    
        f.write("\\hline \n")
        f.write(r"\end{tabular}")


    
sum_menu_byyear=pd.pivot_table(data,values='end_date',index='treament_options',columns='year',aggfunc=np.count_nonzero,fill_value=0)




