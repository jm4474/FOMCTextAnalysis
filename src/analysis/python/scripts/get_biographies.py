#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
READ IN: 
    1) Biography data "../data/speaker_biographies.xlsx"

EXPORT:
    "../output/biographydata.csv"
    
@author: olivergiesecke
"""


import pandas as pd
import numpy as np
import os
import re



df = pd.read_excel("../data/speaker_biographies.xlsx")

df["age"] = np.nan
df["degreelevel"] = np.nan
for idx,row in df.iterrows():
    descr = row["fed_position"]
    linesplit = descr.split("\n")
    date = []
    for pos in linesplit:
        date.append(int(re.search("(\d+)([^\d])(\d+)",linesplit[0])[1]))
        date.append(int(re.search("(\d+)([^\d])(\d+)",linesplit[0])[3]))
        
    begin = min(date)
    end=max(date)

    midyear = (end + begin) / 2

    age =  midyear - row["year_of_birth"]
    #print(idx)
    df.loc[idx,"age"] = age
    
    
    degree = row["degree"]
     



df["d_regional_fed"] = df["d_regional_fed"].apply(lambda x: 1 if (x=="YES") else 0)

df["d_publicsector"] = df["d_publicsector"].apply(lambda x: 1 if (x=="YES") else 0)

df["d_privatesector"] = df["d_privatesector"].apply(lambda x: 1 if (x=="YES") else 0)

df["d_phd"] = df["d_phd"].apply(lambda x: 1 if (x=="YES") else 0)
df["d_master"] = df["d_master"].apply(lambda x: 1 if (x=="YES") else 0)
df["d_black"] = df["d_black"].apply(lambda x: 1 if (x=="YES") else 0)
df["d_female"] = df["d_female"].apply(lambda x: 1 if (x=="YES") else 0)


df["degree"].value_counts().reset_index().rename(columns={"index":"Degree","degree":"Count"}).to_latex("../output/overleaf_files/tab_degrees.tex",index=False)

pd.options.display.float_format = '{:.2f}'.format
  
sumstats = df[["age","d_phd","d_master","d_black","d_female","d_publicsector","d_privatesector"]].describe().T.reset_index()
sumstats["count"] = sumstats["count"].apply(np.int64)
sumstats= sumstats[['index', 'mean','50%', 'std', 'min', '25%', '75%', 'max', 'count']]

# Renaming
sumstats.rename(columns={'index':"Variable","mean":"Mean","std":"Std","min":"Min","25%":"p25","50%":"Median",'75%':"p75",'max':"Max", 'count':"Count"},inplace=True)

sumstats["Variable"] = sumstats["Variable"].replace({'age':"Age", 'd_phd':"$\mathcal{I}_{\text{PhD}}$", 
                                                     'd_master':r"$\mathcal{I}_{\text{Master}}$", 'd_black':"$\mathcal{I}_{\text{Black}}$",
                                                     'd_female':"$\mathcal{I}_{\text{Female}}$",'d_publicsector':"$\mathcal{I}_{\text{Public Sector}}$",
                                                     'd_privatesector':"$\mathcal{I}_{\text{Private Sector}}$"})

sumstats.to_latex("../output/overleaf_files/tab_sumstats.tex",index=False,escape=False)

df.to_csv("../output/biographydata.csv")