#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
READ IN: 
    1) Angrist Kuersteiner Jorda Data "../../../AKJ_Replication/Replication/data/data_replication.csv"
    2) Alternative data "../output/alternativedata.csv"
      
EXPORT:
    "../output/alternativedata.csv"
    
@author: olivergiesecke
"""


import pandas as pd
import numpy as np
import os
import re



ref_df = pd.read_csv("../output/alternativedata.csv")
ref_df["start_date"] = pd.to_datetime(ref_df["start_date"])
ref_df["end_date"] = pd.to_datetime(ref_df["end_date"])

dates = ref_df.drop_duplicates("start_date", "first")["start_date"].reset_index()
dates["year"] = dates.start_date.apply(lambda x:x.year)
dates["month"] =dates.start_date.apply(lambda x:x.month)
dates["dup"] = dates.duplicated(subset=["year","month"])
print(f"Number of duplicates in therms of year and month: {dates['dup'].sum()}")
dates.drop(columns="dup",inplace=True)

econ_df = pd.read_csv("../../../AKJ_Replication/Replication/data/data_replication.csv")

econ_df["start_date"] = pd.to_datetime(econ_df["date"])

econ_df["year"] = econ_df.start_date.apply(lambda x:x.year)
econ_df["month"] =econ_df.start_date.apply(lambda x:x.month)
econ_df["dup"] = econ_df.duplicated(subset=["year","month"])
print(f"Number of duplicates in therms of year and month: {econ_df['dup'].sum()}")
econ_df.drop(columns=["dup","start_date","date"],inplace=True)

merged = dates.merge(econ_df,on=["year","month"],how="left")

merged.to_csv("../output/econonomicdata.csv",index=False)