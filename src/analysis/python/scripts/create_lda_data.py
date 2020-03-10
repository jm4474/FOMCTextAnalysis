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


def clean_data(alternatives,speakers,votingrecord,speakerid,begin_date,end_date):
            # Alternatives
    alternatives = alternatives[["start_date","alt a corpus","alt b corpus","alt c corpus"]]
    names = {"alt a corpus":"corpus_alta","alt b corpus":"corpus_altb","alt c corpus":"corpus_altc"}
    alternatives.rename(columns=names,inplace=True)
    alts = pd.wide_to_long(alternatives,stubnames="corpus", sep="_",i="start_date", j="alternatives", suffix='\w+')
    alts=alts.reset_index()
    alts.rename(columns={'start_date':'Date','alternatives':'Speaker','corpus':'content'},inplace=True)
    
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
    
        # Merge voting record
    data = data.merge(votingrecord,on=["speaker_id","date"],how="left",indicator=True,sort=False)
    data.dropna(subset=["content"],inplace=True,axis=0)
    data.fillna(value={'votingmember':0, 'ambdiss':0,'tighterdiss':0, 'easierdiss':0},inplace=True)
    data.drop(columns="_merge",inplace=True)
    
        # Contrain dataset
    newdata = data[(data["date"]>begin_date) & (data["date"]<end_date) ]

    return newdata

def main():
    # Load dictionary
    with open('../output/data.json', 'r') as speakerids:
        speakerid = json.load(speakerids)
    
    # Load votingrecord
    votingrecord = pd.read_csv("../output/votingrecord.csv")
    
    # Load speaker text
    speakers = pd.read_csv("../output/speaker_data/speaker_corpus.csv")
    
    # Alternatives that Anand collected
    alternatives = pd.read_csv("../output/alternative_outcomes_and_corpus.csv")
    
    begin_date = "1988-01-01"
    end_date = "2008-12-31"
    
    dataout = clean_data(alternatives,speakers,votingrecord,speakerid,begin_date,end_date)
    
    return dataout

data = main()

# Number of alternatives is 168 in subperiod
len(data.loc[data["d_alt"]==1,'date'].unique())

# Number of transcripts is 234
len(data.loc[data["d_alt"]==0,'date'].unique())


# Determine whether we have transcripts for each date of alternative
new_alt = data.loc[data["d_alt"]==1,'date'].drop_duplicates().reset_index()
new_speeches = data.loc[data["d_alt"]==0,'date'].drop_duplicates().reset_index()
new = new_alt.merge(new_speeches,on="date",how="outer")


with open('../output/data.json', 'r') as speakerids:
    speakerid = json.load(speakerids)

# Load votingrecord
votingrecord = pd.read_csv("../output/votingrecord.csv")

# Load speaker text
speakers = pd.read_csv("../output/speaker_data/speaker_corpus.csv")

# Alternatives that Anand collected
alternatives = pd.read_csv("../output/alternative_outcomes_and_corpus.csv")

begin_date = "1988-01-01"
end_date = "2008-12-31"

alternatives = alternatives[["start_date","alt a corpus","alt b corpus","alt c corpus"]]
names = {"alt a corpus":"corpus_alta","alt b corpus":"corpus_altb","alt c corpus":"corpus_altc"}
alternatives.rename(columns=names,inplace=True)
alts = pd.wide_to_long(alternatives,stubnames="corpus", sep="_",i="start_date", j="alternatives", suffix='\w+')
alts=alts.reset_index()


data =alts.merge(new_speeches,left_on='start_date',right_on='date',how='left')






