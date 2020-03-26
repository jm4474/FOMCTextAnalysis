#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: olivergiesecke
1) Collect the data on the speakers and text for each alternative.
2) Do the regular pre-processing for each text entry.
3) Apply standard LDA
4) Provide summary statics how the probability mass lines up with the different alternatives.
5) Check alignment with the voting record.
"""
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
from gensim.utils import simple_preprocess
import itertools  
import os
import json


###############################################################################


def clean_data(alternatives,speakers,votingrecord,alternative_results,speakerid,begin_date,end_date):
            # Alternatives
    alternatives = alternatives[["start_date","date","alt a corpus","alt b corpus","alt c corpus","alt d corpus"]]
    names = {"alt a corpus":"corpus_alta","alt b corpus":"corpus_altb","alt c corpus":"corpus_altc","alt d corpus":"corpus_altd","date":"end_date"}
    alternatives.rename(columns=names,inplace=True)
    alts = pd.wide_to_long(alternatives,stubnames="corpus", sep="_",i="start_date", j="alternatives", suffix='\w+')
    alts=alts.reset_index()
    alts.rename(columns={'start_date':'Date','alternatives':'Speaker','corpus':'content'},inplace=True)
    #print(alts)
   
    data = pd.concat([speakers,alts],axis=0,keys=[0, 1])
    data = data.reset_index()
    data.drop(columns=["Unnamed: 0","level_1"],inplace=True)
    data.rename(columns={"level_0":"d_alt"},inplace=True)
    
        # Create full speaker dictionary that contains non-voting memebers 
    speakerid = {k.lower():v for k,v in speakerid.items()}
    
    speakers = data['Speaker'].unique().tolist()
    speakers =[s.lower() for s in speakers ]
    
    newspeakerids = {}
    for idx,speaker in enumerate(speakers):
        if speaker in speakerid.keys():
            newspeakerids.update({speaker:speakerid[speaker]})
        else:
            newid="id_"+str(100+idx)
            #print(newid)
            newspeakerids.update({speaker:newid})
            
    #sorted(list(newspeakerids.keys()))
    #sorted([ int(i.strip('id_')) for  i in sorted(list(newspeakerids.values()))])
        
        # Clean dataset
    data["speaker"] = data["Speaker"].apply(lambda x: x.lower())
    data["speaker_id"] = data["speaker"]
    data.replace({"speaker_id":newspeakerids},inplace=True)
    data.drop(columns="Speaker",inplace=True)
    data.rename(columns={"Date":"date"},inplace=True)
    
        # Merge alternative outcomes
    data = data.merge(alternative_results,left_on = "end_date",right_on='date',how="left",indicator=True)
    data.drop(columns=[ 'Unnamed: 0'],inplace=True)
    
        # Merge voting record
    data = data.merge(votingrecord,left_on=["speaker_id","end_date"],right_on=["speaker_id","date"],how="outer",indicator=False,sort=False)
    data.dropna(subset=["content"],inplace=True,axis=0)
    data.fillna(value={'votingmember':0, 'ambdiss':0,'tighterdiss':0, 'easierdiss':0},inplace=True)
    data.drop(columns=["start_date","date_y","date"],inplace=True)
    data.rename(columns={"date_x":"start_date"},inplace=True)
    
    data.loc[(data['votingmember']==1) & (data["_merge"]=='both') ,'act_vote'] = data.loc[(data['votingmember']==1) & (data["_merge"]=='both') ,'act_chosen']
    data.loc[(data['votingmember']==1) & (data['tighterdiss']==1) & (data["_merge"]=='both'),'act_vote'] = data.loc[(data['votingmember']==1) & (data['tighterdiss']==1) & (data["_merge"]=='both'),'vote_tighter']
    data.loc[(data['votingmember']==1) & (data['tighterdiss']==1) & (data['vote_tighter'].isna()) & (data["_merge"]=='both'),'act_vote'] = "tighterdiss"
    data.loc[(data['votingmember']==1) & (data['easierdiss']==1) & (data["_merge"]=='both'),'act_vote'] = data.loc[(data['votingmember']==1) & (data['easierdiss']==1)& (data["_merge"]=='both'),'vote_easier']
    data.loc[(data['votingmember']==1) & (data['easierdiss']==1) & (data['vote_easier'].isna()) & (data["_merge"]=='both'),'act_vote'] = "easierdiss"
    data.loc[(data['votingmember']==1) & (data['ambdiss']==1) & (data["_merge"]=='both'),'act_vote'] = "ambdissent"
    data.drop(columns = ["_merge"],inplace=True)
    
        # Constrain dataset
    newdata = data[(data["start_date"]>=begin_date) & (data["start_date"]<=end_date) ]

    return newdata

def main():
    # Load dictionary
    with open('../output/data.json', 'r') as speakerids:
        speakerid = json.load(speakerids)
    
    # Load votingrecord
    votingrecord = pd.read_csv("../output/votingrecord.csv").sort_values(by="date")
    
    # Load speaker text
    speakers = pd.read_csv("../output/speaker_data/speaker_corpus.csv").sort_values(by="Date")
    speakers = speakers[speakers.FOMC_Section==2]

    # Alternatives that Anand collected
    alternatives = pd.read_csv("../output/alternative_outcomes_and_corpus.csv")
    
    # Alternative results
    alternative_results = pd.read_csv("../output/alternative_results.csv")
    
    begin_date = "1988-03-29"
    end_date = "2006-01-31"
    
    dataout = clean_data(alternatives,speakers,votingrecord,alternative_results,speakerid,begin_date,end_date)
    
    return dataout
# =============================================================================
# # ### Do a variety of checks on the data
# 
# data = main()
# print("The total data length is: %s" % len(data))   
#
# num = len(data.loc[data["d_alt"]==1,'start_date'].unique())
# print(f"Alternative dates: {num} of 168")
# 
# num = len(data.loc[(data["d_alt"]==0) & (data["votingmember"]==1) ,'start_date'].unique())
# print(f"Dates with votes: {num} of 174")
#  
# num =len(data.loc[(data["d_alt"]==0) & (data["votingmember"]==1)])
# print(f"Votes: {num} out of 1905")
#  
# # Check the number of dissents tighter
# num =len(data.loc[(data["d_alt"]==0) & (data["tighterdiss"]==1)])
# print(f"Dissent tighter: {num} out of 57")
# 
# # Check the number of dissents easier
# num =len(data.loc[(data["d_alt"]==0) & (data["easierdiss"]==1)])
# print(f"Dissent tighter: {num} out of 23")
# 
# # Check the number of dissents easier
# num =len(data.loc[(data["d_alt"]==0) & (data["ambdiss"]==1)])
# print(f"Dissent tighter: {num} out of 14")
# 
# 
# # Check for the missing votes
# new = data.loc[(data["d_alt"]==0) & (data["votingmember"]==1)].pivot_table(index="end_date",values="votingmember",aggfunc=sum).reset_index()
# excel_df = pd.read_excel("../data/fomc_dissents_data.xlsx",skiprows=3)
# excel_df['FOMC Votes'] = excel_df['FOMC Votes'].apply(lambda x:0 if np.isnan(x) else x)
# excel_df['date'] = excel_df["FOMC Meeting"].dt.date
# excel_df = excel_df[~excel_df["Chair"].isna()]
# new["end_date"] = pd.to_datetime(new["end_date"]).dt.date
# newn = new.merge(excel_df,left_on="end_date",right_on="date",how="left")
# newn['dev'] = newn['FOMC Votes'] == newn['votingmember']
# bb = newn[newn['dev']==False]
# check = data[data['end_date']=="2007-06-28"]
# ## All of the missing votes are on 01/05/1988: Voters don't have interjections. 
# ## This is a date without bluebooks. Hence voting record is complete.
#
# data['new']=1
# df_balt=data[data['d_alt']==1].pivot_table(index="date",values='new',aggfunc=np.sum).reset_index()
# df_summary = data.pivot_table(index="date",values='new',columns=['d_alt','votingmember'],aggfunc=np.sum)
#  
# =============================================================================









