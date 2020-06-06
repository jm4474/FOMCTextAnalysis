#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
READ IN: 
    1) Manual Bluebook Extraction "../data/bluebook_manual_data_online_WORKING.xlsx"
    2) Missing Bluebook Alternatives "../data/bluebook_missingalternatives.xlsx"
    3) FFR Target "../../../collection/python/data/FRED_DFEDTAR.xls"
    4) Meeting Dates "../../../collection/python/output/derived_data.csv"
@author: olivergiesecke
"""


import pandas as pd

def map_treatment(x):
    if x == 0:
        treat = "U"
    elif x> 0:
        treat = "T"
    else:
        treat = "E"
    return treat

def build_altmenu(blue_df,bb_missing_df):
    blue_df['start_date'] = pd.to_datetime(blue_df['start_date'])
    
        # Select columns
    selectcols = ['start_date'] + [f'C_TREATMENT_alt_{alt}' for alt in ['a','b','c','d','e']] + [f'justify_alt_{alt}' for alt in ['a','b','c','d','e']] + [f'C_TREATMENT_SIZE_alt_{alt}' for alt in ['a','b','c','d','e']]
    blue_df = blue_df[selectcols]
        
        # Reshape long
    longalt_df = pd.wide_to_long(blue_df, ['C_TREATMENT_alt','C_TREATMENT_SIZE_alt', 'justify_alt' ], i='start_date', j="alternative", sep="_", suffix='\w+') 
    longalt_df  =longalt_df.reset_index()
    
        # Restrict time period
    longalt_df = longalt_df[(longalt_df['start_date']>="1988-01-01") & (longalt_df['start_date']<="2008-12-31")]                    
    longalt_df = longalt_df[(longalt_df['start_date']<"2001-03-20") | (longalt_df['start_date']>"2004-01-29")]
    longalt_df = longalt_df.sort_values(by=["start_date","alternative"])
    
        # Cleaning
    longalt_df.drop(columns='justify_alt',inplace=True)
    longalt_df.rename(columns={"C_TREATMENT_alt":"treatment",'C_TREATMENT_SIZE_alt':"size"},inplace=True)
    
    
        # Fill-in the missing corpora for time 3/20/01 - 1/27/04
    bb_missing_df['start_date'] = pd.to_datetime(bb_missing_df['date'])
    bb_missing_df.drop(columns=["date",'alt_num'],inplace=True)
    bb_missing_df.rename(columns={'alt':'alternative', 'change':"size"},inplace=True)
    
    all_df = pd.concat([bb_missing_df,longalt_df],join="outer",axis=0,ignore_index=True)
    
    all_df = all_df[['start_date','alternative','size']]
    all_df = all_df.sort_values(by=["start_date","alternative"])
    
    all_df = all_df[~all_df['size'].isna()]
    all_df = all_df[all_df['size']!="N"]
    all_df.reset_index(drop=True,inplace=True)
    
    # Assign treatment 
    all_df['treatment'] = all_df['size'].map(map_treatment)
    return all_df

def build_alttext(blue_df,bb_missing_df):
    blue_df = pd.read_excel("../data/bluebook_manual_data_online_WORKING.xlsx")
    bb_missing_df=pd.read_excel("../data/bluebook_missingalternatives.xlsx")
    
    blue_df['start_date'] = pd.to_datetime(blue_df['start_date'])
        
        # Select columns
    selectcols = ['start_date'] + [f'Sentences_alt_{alt}' for alt in ['a','b','c','d','e']] + [f'C_TREATMENT_SIZE_alt_{alt}' for alt in ['a','b','c','d','e']]
    blue_df = blue_df[selectcols]
        
        # Reshape long
    longalt_df = pd.wide_to_long(blue_df, ['Sentences_alt',"C_TREATMENT_SIZE_alt"], i='start_date', j="alternative", sep="_", suffix='\w+') 
    longalt_df  =longalt_df.reset_index()
    
        # Restrict time period
    longalt_df = longalt_df[(longalt_df['start_date']>="1988-01-01") & (longalt_df['start_date']<="2008-12-31")]                    
    longalt_df = longalt_df[(longalt_df['start_date']<"2001-03-20") | (longalt_df['start_date']>"2004-01-29")]
    longalt_df = longalt_df.sort_values(by=["start_date","alternative"])
    
    longalt_df = longalt_df[~longalt_df['C_TREATMENT_SIZE_alt'].isna()]
    longalt_df = longalt_df[longalt_df['C_TREATMENT_SIZE_alt']!="N"]
    longalt_df.drop(columns=["C_TREATMENT_SIZE_alt"],inplace=True)
    
        # Cleaning
    longalt_df.rename(columns={"Sentences_alt":"text"},inplace=True)
    
    
        # Fill-in the missing corpora for time 3/20/01 - 1/27/04
    bb_missing_df['start_date'] = pd.to_datetime(bb_missing_df['date'])
    bb_missing_df.drop(columns=["date",'alt_num','change'],inplace=True)
    bb_missing_df.rename(columns={'alt':'alternative', },inplace=True)
    
    all_df = pd.concat([bb_missing_df,longalt_df],join="outer",axis=0,ignore_index=True)
    
    all_df = all_df[['start_date','alternative','text']]
    all_df = all_df.sort_values(by=["start_date","alternative"])
    all_df.reset_index(drop=True,inplace=True)
    return all_df
          
def get_ffr(ffr,startyear,endyear):
    ffr.rename(columns={"observation_date":"date","DFEDTAR":"ffrtarget"},inplace=True)
    ffr['year']=ffr['date'].apply(lambda x: x.year)
    ffr=ffr[(ffr['year']>=startyear) & (ffr['year']<=endyear)]
    ffr['target_before'] = ffr['ffrtarget'].shift(1)
    ffr['target_after'] = ffr['ffrtarget'].shift(-1)
    ffr['target_change'] = ffr['target_after'] - ffr['target_before']
    return ffr

def main():
    print("Processing of the manual bluebook menu")
    blue_df = pd.read_excel("../data/bluebook_manual_data_online_WORKING.xlsx")
    bb_missing_df=pd.read_excel("../data/bluebook_missingalternatives.xlsx")
    menu_df = build_altmenu(blue_df,bb_missing_df)
    
    print("Processing Anand and Oliver Alternative Text")
    blue_df = pd.read_excel("../data/bluebook_manual_data_online_WORKING.xlsx")
    bb_missing_df=pd.read_excel("../data/bluebook_missingalternatives.xlsx")
    text_df = build_alttext(blue_df,bb_missing_df)
    
    
    print("Import FFR Target")
    startyear, endyear = 1988, 2008
    ffrdata=pd.read_excel("../../../collection/python/data/FRED_DFEDTAR.xls",skiprows=10)
    ffr = get_ffr(ffrdata,startyear,endyear)
    
    print("Processing the Ambiguous Decisions")
    decisions_df = pd.read_excel("../data/undetermined_alternatives_og.xlsx")
    decisions_df = decisions_df.loc[~decisions_df["Final decision"].isna(),['start_date',"Final decision"]].rename(columns={"Final decision":'decision'})
    
    dates_df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    dates_df['start_date'] = pd.to_datetime(dates_df['start_date'])
    dates_df['end_date'] = pd.to_datetime(dates_df['end_date'])
    dates_df = dates_df.drop_duplicates(subset="start_date")
    
    merged_df = menu_df.merge(dates_df[["start_date","end_date"]],on="start_date",how="left")
    
    merged_df = merged_df.merge(ffr,left_on="end_date",right_on="date",how="left")
    
    merged_df = merged_df.merge(decisions_df,on="start_date",how="left")

    merged_df = merged_df[['start_date','end_date','alternative','size','treatment','ffrtarget', 'target_before', 'target_change', 'decision']]

    merged_df['newds'] = merged_df.loc[ merged_df['size']== merged_df["target_change"],'alternative' ]

    helpdf = merged_df.loc[(~merged_df['newds'].isna()) & (merged_df['decision'].isna()),['start_date','newds']]
    helpdf.rename(  columns = {'newds':"matchdec"},inplace=True)

    merged_df =  merged_df.merge(helpdf,on="start_date",how="left")
    merged_df.loc[ merged_df['decision'].isna(),'decision'] = merged_df.loc[ merged_df['decision'].isna() , 'matchdec']
    merged_df.drop(columns=['newds',"matchdec"],inplace=True)
    
    mergedtext_df = merged_df.merge(text_df,on=["start_date","alternative"],how="inner")
    
    print("Export the final dataset")
    mergedtext_df.to_csv("../output/alternativedata.csv",index=False)